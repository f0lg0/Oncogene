# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

# Note
This changelog is pretty "young", I didn't keep it when I started the projects a long while ago.

## [Released]
## [0.6.0] - 2020-04-12
## Added
- support for Linux targets

## [0.5.0] - 2020-04-11
## Added
- handled ConnectionResetError for more stability
- sleep functions to avoid buffer congestion

## [0.4.0] - 2020-04-10
### Added
- More stability in case of force quit

## [0.3.0] - 2020-04-07
### Added
- feature to hide the keylogger files
- comments inside the code to explain it better

## [0.2.0] - 2020-03-30
### Added 
- Sleep functions to avoid congesting the buffer while sending commands fast.

## [0.1.0] - 2020-03-29
### Added
- "Reapeat in case of error" to the download feature so the program doesn't crash
- Support for KeyboardInterrupt while receiving the keylogger logs (you can ctrl + c).
### Changed
- '?' to '#' inside checkConnection() due to the fact thath there's a chance of it getting added to python scripts [ UPDATE: FIXED  -> this was caused by buffer congestion ]
