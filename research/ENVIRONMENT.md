# Development environment

Inspected on 25 November 2026 in `D:\Projekty\D2MapPredicter`.

| Item | Observed |
| --- | --- |
| OS and shell | Windows 10 Pro 22H2 x64, build 19045.6466. Windows PowerShell 5.1. |
| Editor | VS Code 1.147.0 x64. |
| Version control | Git 2.39.2.windows.1. The directory is outside a Git worktree. |
| C# | The `dotnet` command and SDK were absent from `PATH` and the checked machine and per-user install locations. A .NET Framework 4.8-family runtime is present. |
| Python | `python` runs Python 3.11.5 x64 directly. The `py` launcher reports no installation. |
| Other tools | Node.js 24.13.1, npm 11.16.0 via `npm.cmd`, and ripgrep 15.2.0. Zig, Go, CMake and `cl` were absent from `PATH`. Visual C++ workload availability was not checked. |
| Workspace data | Initially empty. No local game data, generated maps, or independently annotated D2R fixtures were supplied. Game installation and asset entitlement were not inspected. |
| Network | The research browser reached public sources. Direct GitHub API requests from PowerShell could not connect in this environment. |

Recommended production stack is **C# with .NET 10 LTS x64** on a supported Windows environment. Microsoft's current modern .NET matrix limits Windows 10 support to qualifying LTSC and Enterprise releases. This machine reports Windows 10 Pro 22H2. Whether the SDK would run locally has not been tested. The installed Python is sufficient for the offline algorithm experiment while the supported C# build environment is resolved. [Microsoft's Windows matrix](https://learn.microsoft.com/en-us/dotnet/core/install/windows), [Microsoft's .NET lifecycle](https://learn.microsoft.com/en-us/lifecycle/products/microsoft-net-and-net-core)

No dependencies were installed. No generator was built, imported or executed. If Phase 1 proceeds, use Python 3.11 and its standard library for the experiment when a supported C# environment is unavailable. Check generator-specific toolchain, input assets and offline package availability only if the classic reference export is attempted.
