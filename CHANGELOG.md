# [0.5.0](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v0.4.0...v0.5.0) (2022-11-23)


### Bug Fixes

* **apply:** fixes apply without workers flag behaviour ([a6b1d71](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/a6b1d71fa37b12d26d627428d1fdc8cd163418eb))
* **apply:** fixes guid_functor for network ([0831a0c](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/0831a0c929d436361eade5338b540efe034ad08c))
* **config:** new_client without project now does not read project from config ([7c2c5fd](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/7c2c5fd3c9330f4df38e7160083cbcd81a8a7fb4))
* **package:** fixes several issues with rending packages from apply manifests ([c1acc1e](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/c1acc1eae09c8002df7cfb0e92aa0526f4d721d4))


### Features

* **project:** adds support for specifying organization in create project command ([#54](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/54)) ([39f19b6](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/39f19b6548df7478f85cb78a864365597774fb3a)), closes [#48](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/48)

# [0.4.0](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v0.3.1...v0.4.0) (2022-10-03)


### Bug Fixes

* **network:** handles network not found correctly ([#22](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/22)) ([b38c7a0](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/b38c7a04e6d3672254537eacec23cea1e04f8ff2))
* **shell:** Fixed a bug which causes REPL to close in case of exception. ([e8dc6f0](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/e8dc6f06cb57aab42dce55f4d7d5b2f468d3a9d1))


### Features

* **apply:** adds support for apply command ([#30](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/30)) ([f6ae40d](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/f6ae40dac8dfdff2343fa52b299fa4bd0dfc7be0)), closes [#39](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/39)
* **auth:** adds support for non-interactive login ([#32](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/32)) ([8c8c460](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/8c8c46084487d7b50d09cad6fdb97b2d54326746))
* **project:** adds highlight for current project in list output ([ce348da](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/ce348da36a2d61ec6709d34ff46f1ff0289aa986))
* **shell:** adds improvements in repl session ([b7a481e](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/b7a481e58635f1c0f40ae79a5240f928b4a95683))

## [0.3.1](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v0.3.0...v0.3.1) (2022-03-29)


### Bug Fixes

* **auth:** fixes import error for read_config ([#19](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/19)) ([d2534e0](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/d2534e03a85661f3c68c10add44a4f48d8ecac88))

# [0.3.0](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v0.2.0...v0.3.0) (2022-03-24)


### Bug Fixes

* **device:** disable yamux switch for tunnel ([2c97119](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/2c971197413c2444dd2af1819be6becf68420e04))
* **network:** makes device flag optional ([c9d8305](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/c9d8305002a8ce07d57ecff6759d07d421550736))


### Features

* added initial support for plugins ([c513315](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/c5133151a33e0c4e368048ef2d57de3551ebac5f))
* **auth:** adds support for ephemeral environments ([71187ab](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/71187ab95d0d0c06bfb3a933aca7b3c04b7f998b))

# [0.2.0](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v0.1.1...v0.2.0) (2021-12-27)


### Bug Fixes

* **device:** convert PosixPath to str ([#1](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/1)) ([5346e54](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/5346e54dc61af272b10ac1a5485f60802cb7acc6))
* **device:** fixes the device inspect command ([5f76295](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/5f76295bdb751c240441b8f4e627501a7a86de20))
* **network:** ROS distro is corrected to noetic ([#7](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/7)) ([837352b](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/837352b2272ded8cc1ee7dc9d1ad70f18b85e212))
* **package:** fixes handling for wrong name ([4607022](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/4607022a745aa247fb9fd1ba6bf3804370c9ea02))
* **static-route:** fixes the name to guid behaviour for hyphenated names ([7bd5b8e](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/7bd5b8edacfba278426a6fd2182a06cd5ce2f52c))


### Features

* **marketplace:** support for marketplace bulk install ([182fab9](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/182fab9e6625b22bb3ca1a987d884bb831217466))
* **network:** adds device native network support ([020b096](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/020b096d34325b901e66e2152faa271d7754f5b4))

## [0.1.1](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v0.1.0...v0.1.1) (2021-10-28)


### Bug Fixes

* **setup.py:** set markdown type long description ([39c5bd3](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/39c5bd380875c09db75eb62c3408e149a0e76645))

# [0.1.0](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v0.0.1...v0.1.0) (2021-10-28)
