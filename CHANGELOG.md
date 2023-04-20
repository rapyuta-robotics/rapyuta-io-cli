# [2.0.0](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v1.0.0...v2.0.0) (2023-04-20)


### Bug Fixes

* **apply:** apply_async hangs when worker raises exception ([fc5deee](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/fc5deeef9051401c70ca3929ed47762ec52e29c4))
* **apply:** fixes the schema not found errors ([d4847a5](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/d4847a53c7b103e8d4400f5c815ea6e5cb5b60f6))
* **apply:** skips confirmation during dry run ([9e1858a](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/9e1858a0d3b0943a9b38775f312a6200891cd00a))
* **deployment:** adds deployment as component alias to avoid conflicts ([861301e](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/861301ef58b654836634615b75c7e196fadf4bf9))
* **gh-actions:** code quality workflow does not comment on pr ([56de428](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/56de428e67f3badc911ccef1dcd8ec900ff591f1))
* **network:** adds _get_limits method for cloud routed network. ([4751307](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/4751307e53f554904184527271b4ba133a5e7d73))
* **network:** adds wait until network is ready for Apply ([897a134](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/897a134259f15b22dc1b137704e5747914dd3da3))
* **parameter:** handles the non-directory tree names ([bbf65f2](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/bbf65f22585925241d4a99179025e2ef09c55af1))
* **secret:** removes unwanted required field in json schema ([beb1730](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/beb1730b1c4d361c60ab1c2528f0a95cfeb8f2b0))
* updates conventional-commit workflow ([886e02a](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/886e02a6716bfe8644bacbc3ddcc84bcca51b8e6))


### Code Refactoring

* **parameter:** improves the user-experience ([b132247](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/b13224708c3e8133fd5cc8b9bcdcd3fab01a1d39))


### Features

* **apply:** improves validation error messages ([8ce51f4](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/8ce51f487d9ec6ceffc9a0dd7374dbbaef8ba2be))
* **deployment:** prints deployment error details ([c3fbf33](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/c3fbf3334d7af2181675e2a3084a75ee7378ff05))
* **network:** adds support for fractional resource limits ([b7e5b57](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/b7e5b57a653851a06016f067a86ecb23a75f74d6))
* **parameter:** adds option to upload config as FolderNodes ([28af86e](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/28af86e812b3a8154c3f6dfe46073d10eb6b9ae8))
* **utils:** adds decorator for yaspin spinner ([a4e96a1](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/a4e96a126954b4d36d3e48df99a3048c3b03951d)), closes [#113](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/113)


### BREAKING CHANGES

* **parameter:** This commit changes the public API of the parameter
command.

# [1.0.0](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v0.6.0...v1.0.0) (2023-02-07)


### Bug Fixes

* **config:** update default piping server address ([e3a4ed4](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/e3a4ed4bc203d004706bcb38c04cd07856ac215a))
* **deployment:** speed up  command ([37843fa](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/37843fa601309ebce1105ecb9d67ad54b0501e3f))
* **package:** rename topic qos from medium to med ([cb8fd68](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/cb8fd68482d06e165bda7e1ebde0362f09818159))
* **package:** update executable limits validation ([4a65759](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/4a65759fd4348a05564d6bd5317c1209ca5c841e))
* **package:** validate `image` name for executables ([#82](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/82)) ([c01127b](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/c01127b0f69182127ecf1a562367b6bd68cd1065))


### Features

* **apply:** confirms before apply and delete ([363fd87](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/363fd87c6f8f867c39678c21118cd8fc8e341383))
* **auth:** support io-dev environment ([#81](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/81)) ([2a9e4b6](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/2a9e4b6c61c738afe5c87924e24f7b5ac724bed5))
* **cli:** sort lists based on human-readable names ([6f46cc1](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/6f46cc14b3a569a5498e8be6d507ece083f1b266))
* **cli:** tabulate list commands ([53b840e](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/53b840e3998aebfe6d82a31949613cb2da97f8fd))
* **device:** add support for user-specific ssh-key ([f1cf8d5](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/f1cf8d552a8ec8ba589e259defbb0d0b6af81d88))
* **parameters:** apply config parameters to devices ([35f5a03](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/35f5a034f2bbe5cafe8159b195a6a045b4304102))
* **rosbag:** adds rosbag job inspect command ([8d5556e](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/8d5556ef64ce8a22719ac9b8ab70eb0766888324))


### BREAKING CHANGES

* **apply:** adds confirmation before the `rio apply` and `rio
delete`. This may break rio cli integration in other tools. Please
update your code to include --silent flag for apply and delete commands
to bypass confirmation prompts.

# [0.6.0](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v0.5.0...v0.6.0) (2022-12-14)


### Bug Fixes

* **build:** fixes broken apply for builds ([a68f7d0](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/a68f7d077e4f4442952f61556bd4b9204cc63fe8))
* **project:** fixes project creation ([e89a1b4](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/e89a1b41b610981828a49c5d42dc1bde72a3cb31))


### Features

* **managedservice:** add support for rapyuta.io `managedservices` ([7aff123](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/7aff123997502af885138260dd1b7037160fc42c))
* **rosbags:** adds support in apply packages and deployment, and adds rosbag job update and trigger upload. ([875d50f](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/875d50fd4486dd93514f36a3871a3bf9f7841344))
* **template:** add helm3 template like support ([ceb12c5](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/ceb12c5c12b20618769a44435b946dd73695f661))

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
