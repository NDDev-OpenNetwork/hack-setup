# Flutter, native modules and desktop rules

## Flutter and Dart

Use the Dart SDK bundled with the selected Flutter installation. Record the actual analyzer process used by Serena; its stable adapter may download a different standalone SDK. Do not downgrade the app or invent a Serena Dart executable override to hide this mismatch. Follow the setup compatibility report.

Use Riverpod for shared reactive state, go_router for navigation and Dio through the generated API client. Keep HTTP models generated from the same OpenAPI source as the web client. Freezed models are appropriate for app/domain state where useful, not a second manual copy of generated transport models.

Use Flutter localization/ARB with RU/KK/EN and consistent placeholders. Handle widget disposal, cancellation and post-await mounted/lifecycle checks. Model async loading/error states instead of exposing uninitialized data. Avoid provider-side effects during build and implicit global mutable session state.

Store sensitive app tokens in the intended platform secure-storage layer. Perform OAuth using a system browser and a verified backend return/deep-link flow; do not embed provider secrets. Treat deep links as untrusted inputs. Request camera/microphone/files permissions only for the feature that needs them.

Generated files such as `.g.dart`, `.freezed.dart`, localization outputs and generated SDKs are generator-owned. Use the relevant generator and formatter, not manual patches. Verify Flutter analysis and the affected platform build/run; desktop success does not prove Android/iOS integration.

## Rust and Python extensions

Keep a Cargo workspace and explicit public ownership/error contracts. Use rustfmt and selected Clippy checks. Avoid panics at user-controlled boundaries, unbounded allocation and blocking work inside async executors. `unsafe` requires a concrete invariant and review of the call boundary, not merely a speed justification.

For PyO3/maturin, verify ABI/interpreter compatibility, ownership across the FFI boundary, error conversion and GIL assumptions for the actual build. Do not pass borrowed data across lifetime boundaries. A release build and representative measurement should support a performance claim.

rust-analyzer must see the correct Cargo workspace, features and rust-src. Build scripts/procedural macros can execute code; use the authorized development environment. A successful language-server handshake does not establish target compilation.

## Tauri

Reuse the React application where that is the chosen client. Define a narrow typed Rust command surface and explicit Tauri capabilities. Do not expose unrestricted shell/filesystem operations to imported HTML or untrusted web content. Validate IPC input on the Rust side; the frontend type system is not a permission check.

Verify packaging, deep links and platform resources on each target that will be demonstrated. Do not introduce a second desktop implementation when Flutter or Tauri already owns the selected experience.

## Go and other native code

Go is an optional tool/component language, not a requirement to split the backend. Use modules, gofmt, explicit error handling, cancellation and bounded goroutines. gopls must resolve the real module/workspace with the selected toolchain. Avoid duplicate business rules already owned by Python.

For C/C++, Swift, Kotlin or Java bridges, enable only the relevant LSP and native toolchain. Use the actual compilation database/Gradle/Xcode context. Keep generated native artifacts out of hand editing and do not mark an unavailable target platform as tested.
