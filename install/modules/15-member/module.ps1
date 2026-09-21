# Member identity + shared git defaults, native Windows. Twin of
# module.sh -- member is data in the pin (team.members), identity is
# derived from `gh api user` so no personal mail lands in this repo.
# NOTE: keep this file pure ASCII -- Windows PowerShell 5.1 reads ps1
# without BOM as ANSI, and smart quotes from mangled UTF-8 would toggle
# string state (see CI run 35645725406).
$ErrorActionPreference = 'Stop'
. (Join-Path $env:HACK_LIB 'common.ps1')

$PinPath = Join-Path $env:HACK_REPO_ROOT 'build\stack-pin.json'
$Marker = Join-Path $env:HACK_REPO_ROOT '.agent\member'

function Get-MemberList {
    $members = Get-HackPin $PinPath 'team.members'
    if (-not $members) { return '' }
    return ($members.PSObject.Properties.Name) -join ' '
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
    $members = Get-HackPin $PinPath 'team.members'
    $names = @()
    if ($members) { $names = @($members.PSObject.Properties.Name) }
    if ($names -notcontains $Member) {
        Die "unknown member '$Member' - expected one of: $($names -join ', ')"
    }
}

function Get-GhIdentity {
    # @{login; name; email} for the authenticated gh user, or $null.
    $raw = gh api user 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $raw) { return $null }
    # gh api prints multi-line JSON; join before ConvertFrom-Json (PS 5.1
    # pipes each line separately otherwise).
    $u = ($raw -join "`n") | ConvertFrom-Json
    $login = [string]$u.login
    $name = if ($u.name) { [string]$u.name } else { $login }
    $email = [string]$u.email
    if (-not $email) {
        $email = if ($u.id) { "$($u.id)+$login@users.noreply.github.com" } else { "$login@users.noreply.github.com" }
    }
    return @{ login = $login; name = $name; email = $email }
}

function Set-GitDefaults {
    foreach ($section in 'git_defaults', 'windows_git_defaults') {
        $defaults = Get-HackPin $PinPath "team.$section"
        if (-not $defaults) { continue }
        foreach ($prop in $defaults.PSObject.Properties) {
            & git config --global $prop.Name "$($prop.Value)"
            if ($LASTEXITCODE -ne 0) { Die "git config --global $($prop.Name) failed" }
        }
    }
}

function Test-SshGitHub {
    # GitHub answers `ssh -T` with exit 1 + a greeting even on success.
    $out = & ssh -T -o BatchMode=yes -o ConnectTimeout=5 git@github.com 2>&1
    if ("$out" -match 'successfully authenticated') {
        Log "ssh: github.com key ok"
    } else {
        Log "WARN: no github.com SSH key - needed for the vibestrap submodule; ssh-keygen + add to GitHub"
    }
}

function Run-Install {
    $member = Resolve-Member
    Set-GitDefaults
    Log "git defaults applied (ff-only, prune, rerere, zdiff3, lf, longpaths)"

    if (-not $member) {
        $list = Get-MemberList
        Log "WARN: no --member flag - git identity untouched; rerun .\setup.ps1 --member NAME ($list)"
        return
    }
    Assert-KnownMember $member
    $expected = Get-MemberGithub $member

    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
        Die "gh is required for member identity; module 10 should have caught this"
    }
    $id = Get-GhIdentity
    if (-not $id) {
        Die "gh not authenticated - run: gh auth login  (member $member expects @$expected)"
    }
    if ($id.login -ne $expected) {
        Die "gh is authenticated as @$($id.login) but member '$member' is @$expected - run gh auth login first"
    }
    & git config --global user.name $id.name
    & git config --global user.email $id.email
    $name = $id.name
    $email = $id.email
    Log "git identity: $name <$email>"

    & gh auth setup-git 2>$null
    Test-SshGitHub
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Marker) | Out-Null
    [System.IO.File]::WriteAllText($Marker, "$member`n")
    $ghLogin = $id.login
    Log "member: $member (@$ghLogin) - marker at .agent\member"
}

function Run-Status {
    $member = Resolve-Member
    if (-not $member) {
        $list = Get-MemberList
        Log "no member configured - run .\setup.ps1 --member NAME ($list)"
        return
    }
    Assert-KnownMember $member
    $expected = Get-MemberGithub $member
    $id = Get-GhIdentity
    if (-not $id) { Die "gh not authenticated; member $member expects @$expected" }
    if ($id.login -ne $expected) {
        Die "gh login @$($id.login) does not match member $member (@$expected)"
    }
    $name = & git config --global user.name
    $email = & git config --global user.email
    if (-not $name -or -not $email) { Die "git identity unset - run .\setup.ps1 --member $member" }
    $ghLogin = $id.login
    Log "member $member ok: $name <$email>, gh @$ghLogin"
}

function Run-DryRun {
    $member = Resolve-Member
    if ($member) {
        Assert-KnownMember $member
        $expected = Get-MemberGithub $member
        Log "member $member -> expects gh login @$expected"
        Log "would set git user.name/user.email from gh api user (profile name + email/noreply)"
    } else {
        $list = Get-MemberList
        Log "no member selected (.\setup.ps1 --member NAME: $list) - would apply shared git defaults only"
    }
    foreach ($section in 'git_defaults', 'windows_git_defaults') {
        $defaults = Get-HackPin $PinPath "team.$section"
        if (-not $defaults) { continue }
        foreach ($prop in $defaults.PSObject.Properties) {
            Log "would git config --global $($prop.Name) $($prop.Value)"
        }
    }
    Log "would verify ssh -T git@github.com and run gh auth setup-git"
}

$Action = if ($args.Count -gt 0) { $args[0] } else { 'status' }
switch ($Action) {
    'install' { Run-Install }
    'status' { Run-Status }
    'dry-run' { Run-DryRun }
    default { Die "unknown action: $Action" }
}
