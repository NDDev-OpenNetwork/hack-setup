# Member identity + shared git defaults, native Windows. Twin of
# module.sh — member is data in the pin (team.members), identity is
# derived from `gh api user` so no personal mail lands in this repo.
$ErrorActionPreference = 'Stop'
. (Join-Path $env:HACK_LIB 'common.ps1')

$PinPath = Join-Path $env:HACK_REPO_ROOT 'build\stack-pin.json'
$Marker = Join-Path $env:HACK_REPO_ROOT '.agent\member'

function Get-MemberList {
    return ((Get-HackPin $PinPath 'team.members').PSObject.Properties.Name) -join ' '
}

function Get-MemberGithub([string]$Member) {
    return Get-HackPin $PinPath "team.members.$Member.github"
}

function Resolve-Member {
    if ($env:HACK_MEMBER) { return $env:HACK_MEMBER }
    if (Test-Path -LiteralPath $Marker) { return (Get-Content -LiteralPath $Marker -Raw).Trim() }
    return $null
}

function Assert-KnownMember([string]$Member) {
    $names = (Get-HackPin $PinPath 'team.members').PSObject.Properties.Name
    if ($names -notcontains $Member) {
        Die "unknown member '$Member' — expected one of: $($names -join ', ')"
    }
}

function Get-GhIdentity {
    # @{login; name; email} for the authenticated gh user, or $null.
    $raw = gh api user 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $raw) { return $null }
    $u = $raw | ConvertFrom-Json
    $login = [string]$u.login
    $name = if ($u.name) { [string]$u.name } else { $login }
    $email = if ($u.email) { [string]$u.email } else { "$($u.id)+$login@users.noreply.github.com" }
    return @{ login = $login; name = $name; email = $email }
}

function Set-GitDefaults {
    $defaults = Get-HackPin $PinPath 'team.git_defaults'
    foreach ($prop in $defaults.PSObject.Properties) {
        & git config --global $prop.Name "$($prop.Value)"
        if ($LASTEXITCODE -ne 0) { Die "git config --global $($prop.Name) failed" }
    }
    $winDefaults = Get-HackPin $PinPath 'team.windows_git_defaults'
    foreach ($prop in $winDefaults.PSObject.Properties) {
        & git config --global $prop.Name "$($prop.Value)"
        if ($LASTEXITCODE -ne 0) { Die "git config --global $($prop.Name) failed" }
    }
}

function Test-SshGitHub {
    # GitHub answers `ssh -T` with exit 1 + a greeting even on success.
    $out = & ssh -T -o BatchMode=yes -o ConnectTimeout=5 git@github.com 2>&1
    if ("$out" -match 'successfully authenticated') {
        Log "ssh: github.com key ok"
    } else {
        Log "WARN: no github.com SSH key — needed for the vibestrap submodule; ssh-keygen + add to GitHub"
    }
}

function Run-Install {
    $member = Resolve-Member
    Set-GitDefaults
    Log "git defaults applied (ff-only, prune, rerere, zdiff3, lf, longpaths)"

    if (-not $member) {
        Log "WARN: no --member flag — git identity untouched; rerun .\setup.ps1 --member <$(Get-MemberList)>"
        return
    }
    Assert-KnownMember $member
    $expected = Get-MemberGithub $member

    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
        Die "gh is required for member identity; module 10 should have caught this"
    }
    $id = Get-GhIdentity
    if (-not $id) {
        Die "gh not authenticated — run: gh auth login  (member $member expects @$expected)"
    }
    if ($id.login -ne $expected) {
        Die "gh is authenticated as @$($id.login) but member '$member' is @$expected — run gh auth login first"
    }
    & git config --global user.name $id.name
    & git config --global user.email $id.email
    Log "git identity: $($id.name) <$($id.email)>"

    & gh auth setup-git 2>$null
    Test-SshGitHub
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Marker) | Out-Null
    [System.IO.File]::WriteAllText($Marker, "$member`n")
    Log "member: $member (@$($id.login)) — marker at .agent\member"
}

function Run-Status {
    $member = Resolve-Member
    if (-not $member) { Die "no member configured — run .\setup.ps1 --member <name>" }
    Assert-KnownMember $member
    $expected = Get-MemberGithub $member
    $id = Get-GhIdentity
    if (-not $id) { Die "gh not authenticated; member $member expects @$expected" }
    if ($id.login -ne $expected) {
        Die "gh login @$($id.login) does not match member $member (@$expected)"
    }
    $name = & git config --global user.name
    $email = & git config --global user.email
    if (-not $name -or -not $email) { Die "git identity unset — run .\setup.ps1 --member $member" }
    Log "member $member ok: $name <$email>, gh @$($id.login)"
}

function Run-DryRun {
    $member = Resolve-Member
    if ($member) {
        Assert-KnownMember $member
        Log "member $member -> expects gh login @$(Get-MemberGithub $member)"
        Log "would set git user.name/user.email from gh api user (profile name + email/noreply)"
    } else {
        Log "no member selected (.\setup.ps1 --member <$(Get-MemberList)>) — would apply shared git defaults only"
    }
    $defaults = Get-HackPin $PinPath 'team.git_defaults'
    foreach ($prop in $defaults.PSObject.Properties) {
        Log "would git config --global $($prop.Name) $($prop.Value)"
    }
    $winDefaults = Get-HackPin $PinPath 'team.windows_git_defaults'
    foreach ($prop in $winDefaults.PSObject.Properties) {
        Log "would git config --global $($prop.Name) $($prop.Value)"
    }
    Log "would verify ssh -T git@github.com and run gh auth setup-git"
}

$Action = if ($args.Count -gt 0) { $args[0] } else { 'status' }
switch ($Action) {
    'install' { Run-Install }
    { $_ -in 'status' } { Run-Status }
    'dry-run' { Run-DryRun }
    default { Die "unknown action: $Action" }
}
