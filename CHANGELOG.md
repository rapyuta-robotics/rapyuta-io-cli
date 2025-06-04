# [9.10.0](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v9.9.3...v9.10.0) (2025-06-04)


### Features

* **device:** add support for native hwil azure vms ([6d3215c](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/6d3215cdabc6ebe0cdf2267b9903be176061356a))

## [9.9.3](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v9.9.2...v9.9.3) (2025-05-28)


### Bug Fixes

* add libmagic binary package for windows ([c359b2b](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/c359b2bd79a5ef1eb75862528713ce632b8517db))
* **apply:** lazy load ansible modules ([5b57c31](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/5b57c312ccb0013f0c1fea8d1698fe9d72a5e1cf))

## [9.9.2](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v9.9.1...v9.9.2) (2025-05-16)


### Bug Fixes

* **oauth2:** fix compatibility with Python3.8 ([1faf3d0](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/1faf3d0486c9a7c82a79b74bc3286e412c217999))

## [9.9.1](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v9.9.0...v9.9.1) (2025-05-13)


### Bug Fixes

* pin click to 8.0.x ([acbd0ce](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/acbd0ce28530f19e250afca4cc281be823a08452))

# [9.9.0](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v9.8.0...v9.9.0) (2025-05-07)


### Bug Fixes

* **oauth2:** increase default pagination limit to 50 to speed up list ([7ab1d64](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/7ab1d6415f0b82f9daec661384e9abb94850823b))
* **project:** fixes the list and inspect project functionality when no organization is selected ([80908c1](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/80908c175cb75e51fecdc158efcb1bd7b797dbc6))
* **usergroup:** handle case-insensitive email support ([15719f0](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/15719f007f79a63438dea63059b1d2ab05984d9c))


### Features

* **apply:** add context in the output for apply-family of commands ([f2ddad4](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/f2ddad48099c63f115e0ca6e4d0e400575469654)), closes [AB#59533](https://github.com/AB/issues/59533)
* **oauth2:** add oauth2 commands ([1cce2d1](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/1cce2d1d92de202fa0af43387764462ecb209c0f))
* **vpn:** support --force flag for vpn connect command ([e9aa3b4](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/e9aa3b4b622d093106fd07416e739a79e1094a6c)), closes [AB#48205](https://github.com/AB/issues/48205)

# [9.8.0](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v9.7.0...v9.8.0) (2025-04-09)


### Bug Fixes

* **device:** handle empty command in device execute ([84a5c9c](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/84a5c9cb1c8bc6b6973fffc14fb741615bd9d0e1))
* **device:** return non-zero exit code if delete fails for atleast one device ([dfcc7d7](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/dfcc7d739f581b709f11241777e198d902990b71)), closes [AB#51601](https://github.com/AB/issues/51601)
* **devices:** update device schema to support noble ([730e747](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/730e747dd72eb51ef3bb61b6ab4cb1911b57c3e2))
* **organization:** handle no user in add/remove user commands ([1741823](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/1741823007c792b9a5f3f3423f426d4ea359733c))
* **parameter:** raise exception when binary upload fails ([e327ec3](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/e327ec3749bb16b2c011c0911f621120cd016ed5))
* **usergroup:** allow empty description in manifest ([c9f2ee2](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/c9f2ee2ca0b192303ccdb845fb86e45cb4d73d79))


### Features

* **apply:** add support for `--delete-existing` flag ([3939d01](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/3939d013f0440e03fb5c1724185bb1ef0e724fe9))
* **device:** enable vpn on all devices if not provided ([f9ae920](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/f9ae920276924fabf7497b60434ff5907d00b8bf))
* **device:** execute command on multiple devices ([fd6fb25](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/fd6fb253e8e47c27533a02c4ab86abb869f47eb5))
* **vpn:** add flush command ([5ea02ee](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/5ea02ee6d34200478b67d1b7e69c41bc8ad5b0e6))

# [9.7.0](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v9.6.0...v9.7.0) (2025-01-29)


### Bug Fixes

* **cli:** returns success in case deployment, package, secret, route, device, disk, network not found while deleting ([2e7e377](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/2e7e37778c9a7b1931723f9f53c8a4f5594333d0))
* **device:** keep device inspect backwards compatible ([5b198b6](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/5b198b626a60e723d34e1ce7ec46151c97ce3dab)), closes [AB#47896](https://github.com/AB/issues/47896)
* **vpn:** fix connect command with --update-hosts flag ([dadab65](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/dadab65fc596be6341f56b4e90b03ac7ee7770a9))


### Features

* **project:** add support for docker-cache feature ([37aba6c](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/37aba6cf3fc78ba78b1a014fd1dc311741d2228c)), closes [AB#43805](https://github.com/AB/issues/43805)
* **projects:** add dockercache subcommand in features command ([4b78076](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/4b780762ef01280ae0f570178d5fafd6c0e5fa07))
* **vpn:** add device-hostname entry in hosts file ([bd4abe4](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/bd4abe45b1c77f932be186c3dbcd2d42c3f24d81))

# [9.6.0](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v9.5.0...v9.6.0) (2025-01-09)


### Features

* **apply:** add support for multiple interfaces in get_intf_ip filter ([589b53c](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/589b53ca78ae259c18a749ed26750a998cc378ff))
* **package:** supports hostPID for package ([519790a](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/519790a76129de81d4968715d8aaeda47f0029c0))

# [9.5.0](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v9.4.0...v9.5.0) (2024-12-11)


### Features

* **apply:** add support for ansible filters in Jinja2 ([#394](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/394)) ([d590490](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/d59049091011d88ec715f302701e425218ba4d9c)), closes [AB#39151](https://github.com/AB/issues/39151)
* **deployment:** adds an option to block paramsync until ready ([387181c](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/387181cab56c7e5f9e1cf2b535245810cc597515))
* **device:** add option to exec commands asynchronously ([#365](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/365)) ([c6bea52](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/c6bea52209881827ceea6dcd084aa6677f1e014d)), closes [AB#16668](https://github.com/AB/issues/16668)
* **device:** handles failed hwil devices during apply and delete ([94bb48e](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/94bb48e54da70cbd767bd500104f957f429c81f7))

# [9.5.0](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v9.4.0...v9.5.0) (2024-12-11)


### Features

* **apply:** add support for ansible filters in Jinja2 ([#394](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/394)) ([d590490](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/d59049091011d88ec715f302701e425218ba4d9c)), closes [AB#39151](https://github.com/AB/issues/39151)
* **deployment:** adds an option to block paramsync until ready ([387181c](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/387181cab56c7e5f9e1cf2b535245810cc597515))
* **device:** add option to exec commands asynchronously ([#365](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/365)) ([c6bea52](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/c6bea52209881827ceea6dcd084aa6677f1e014d)), closes [AB#16668](https://github.com/AB/issues/16668)
* **device:** handles failed hwil devices during apply and delete ([94bb48e](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/94bb48e54da70cbd767bd500104f957f429c81f7))

# [9.5.0](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v9.4.0...v9.5.0) (2024-12-11)


### Features

* **apply:** add support for ansible filters in Jinja2 ([#394](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/394)) ([d590490](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/d59049091011d88ec715f302701e425218ba4d9c)), closes [AB#39151](https://github.com/AB/issues/39151)
* **deployment:** adds an option to block paramsync until ready ([387181c](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/387181cab56c7e5f9e1cf2b535245810cc597515))
* **device:** add option to exec commands asynchronously ([#365](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/365)) ([c6bea52](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/c6bea52209881827ceea6dcd084aa6677f1e014d)), closes [AB#16668](https://github.com/AB/issues/16668)
* **device:** handles failed hwil devices during apply and delete ([94bb48e](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/94bb48e54da70cbd767bd500104f957f429c81f7))

# [9.4.0](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v9.3.0...v9.4.0) (2024-11-25)


### Features

* add RIO_CONFIG env override ([#391](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/391)) ([705d648](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/705d6485c1ea27f6ab6540f846c1a9f7a677db0f))

# [9.3.0](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v9.2.0...v9.3.0) (2024-11-22)


### Features

* adds option for virtual device expiry ([#387](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/387)) ([b10301a](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/b10301afae712f9f3f2a831236e3f4e749bcdd88)), closes [AB#39668](https://github.com/AB/issues/39668)

# [9.2.0](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v9.1.3...v9.2.0) (2024-11-14)


### Bug Fixes

* **device:** report online devices only ([#382](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/382)) ([bfe7bb3](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/bfe7bb326b522e24e153cb745f925c648d077351))
* **organization:** fixes key error when no org is selected ([#383](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/383)) ([29476ff](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/29476ff87c2728be9ec59d369ede7f0831fd1216))


### Features

* **apply:** adds template func to get interface ip ([#379](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/379)) ([d370826](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/d370826f75a506d09d4be40537e46a28c5f4d4ae))

## [9.1.3](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v9.1.2...v9.1.3) (2024-10-22)


### Bug Fixes

* **apply:** secrets are not merged ([#380](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/380)) ([a05e9db](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/a05e9db05b6db95a64b52d94789d86a716ef73f5))

## [9.1.2](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v9.1.1...v9.1.2) (2024-10-22)


### Bug Fixes

* **apply:** handle dry-run without login ([#377](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/377)) ([ddc0f1a](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/ddc0f1a5b73c63f2e68532f5fe14a9657284be47))

## [9.1.1](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v9.1.0...v9.1.1) (2024-10-22)


### Bug Fixes

* **apply:** deep merge secrets and values ([b7af2b3](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/b7af2b3d2bbee569e55d7568f465af8396b4a32f))

# [9.1.0](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v9.0.4...v9.1.0) (2024-10-21)


### Bug Fixes

* **apply:** merge rio namespace with incoming values ([5141bcf](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/5141bcfd090cd08b14af028152ba839c26a5634b))
* **package:** adds the missing --silent alias for force delete ([d4546a9](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/d4546a973902c10579499c2d6d7f75b83d2a4cb6))
* removes object references of project, static-routes, secret, deployment ([8cb381a](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/8cb381ae90ed300162801053f93b1c167b932392))


### Features

* **apply:** allow mutiple values and secret files ([1cffe09](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/1cffe09638049abd4507bf8b55831ed238c4ad7a)), closes [AB#18436](https://github.com/AB/issues/18436)
* **device:** implements report device command ([#371](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/371)) ([acdde63](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/acdde634181e428b804ec3298733d1aef37d9ac4)), closes [AB#19657](https://github.com/AB/issues/19657)
* **device:** wait until virtual device is online on rapyuta.io ([f6bd3e8](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/f6bd3e868316c8b1b7fce028e2528aa00bb04015)), closes [AB#18043](https://github.com/AB/issues/18043)
* **secret:** implements batch delete with regex pattern ([9b57d69](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/9b57d693d307ef6a2dfe9d1bb52cbb8279b364dd)), closes [AB#18146](https://github.com/AB/issues/18146)
* **static-route:** implements batch delete using regex pattern ([a3b5e92](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/a3b5e92906e1ae29a0797baa08b484abd45affe3)), closes [AB#18146](https://github.com/AB/issues/18146)
* **vpn:** adds option to populate vpn peers in hosts file ([c28b9ce](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/c28b9ce18558d090cc138186d7c14eeb8823fd1a))

## [9.0.4](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v9.0.3...v9.0.4) (2024-10-15)


### Bug Fixes

* pins rapyuta-io version to v1.17.1 ([2cb936c](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/2cb936ce2be50f772fb9b304356b7b32446a21ae))

## [9.0.3](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v9.0.2...v9.0.3) (2024-09-26)


### Bug Fixes

* **auth:** use existing token to refresh if valid ([ea0524f](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/ea0524f8d76fbd05997b2e28ebd8d8eb1c584f36))

## [9.0.2](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v9.0.1...v9.0.2) (2024-09-26)


### Bug Fixes

* **package:** handle empty command string ([370d529](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/370d529a339112a192a63c802b4d88d7afe1f9ef))

## [9.0.1](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v9.0.0...v9.0.1) (2024-09-25)


### Bug Fixes

* **usergroup:** remove emailID validation ([88569d9](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/88569d9da9f686bbd0d34fc1e535b0887f8fe638))

# [9.0.0](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v8.1.0...v9.0.0) (2024-09-25)


### Bug Fixes

* **apply:** prints resource name when apply or delete fails ([1952929](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/1952929dc02149f4c0123eceaf0626b91935ce62))
* **configtree:** corrects typo in error message ([2b0edde](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/2b0eddeab3157922142ebbe6674a7ba657e95568))
* **configtree:** returns error when no files are provided in import ([843b793](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/843b7936095b149b1f01c30e418c9083f5ad7bd3))
* corrects error message for batch delete ops ([48447d4](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/48447d439e12536b7518a7c9a079be69e4c8bcf2))
* **delete:** prints appropriate message when deletionPolicy = retain ([7c76d84](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/7c76d84a2e59373cefa4610b34341f2b4a1165d0))
* **deployment:** add phase filter for list_deployments ([a545c1e](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/a545c1ef1c8ff9dcab9a58ba7de79b5880af6dbe))
* **deployment:** fix deployment commands ([6f2aec2](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/6f2aec2a8f11a1f0568c8337ea8670fc78aeb580))
* **deployment:** inspect deployment with guid ([#349](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/349)) ([a34bd0a](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/a34bd0ac050c44a35ce4f1450a29e68048a91a52))
* **deployment:** replace aggregateStatus with status ([9ae1cee](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/9ae1ceee927d9b91e3c7fd0b63e9af30556f4a73))
* **deployments:** adds stopped at time for deployment list ([7891a5c](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/7891a5c5b863fb74746a0a84e5dfbc871c07d017))
* **deployment:** set replica=0 as default in deployment logs command ([e9f4668](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/e9f4668c19b285ba7c8bc6de2b58fd73aeab285a))
* **deployments:** fix deployment status and wait command ([0e3ea14](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/0e3ea146751c586598943e72f8aeb3ae69f2d8bc))
* **deployments:** fix deployment wait command ([e0ef5ed](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/e0ef5edab026c636c30f3b88cfc14f4b17b31d82))
* **deployments:** implements waiting mechanism for disk and network deployments to reach running state ([7e2f0d4](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/7e2f0d43cde69b0b501d9c21f073df3badcbe4cf))
* **device:** updates client in list device deployments command ([18b4c50](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/18b4c508e03392facaad31a597f2f913182da106))
* **disk:** fix disk commands ([2060d7c](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/2060d7c9c9809fbd6bea57b45e8113ac74041690))
* **disk:** prints a better message when no disks are deleted ([dbe83e4](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/dbe83e4dfa9d377134b2d1e7b921961eddd5cd6f))
* fixes resolver and resource models to work with apply ([8279b77](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/8279b77de3aa1c37bb39ddc8655ca64ddb81efdd))
* **jsonschema:** accepts null value in deployment features ([1791b29](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/1791b29c8d600e9b0d081d7937657cd1eb8e2ba5))
* **jsonschema:** corrects resource GUID regex ([8252a71](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/8252a71fa2e455b47cb12f059fbd33586c7d1384))
* **jsonschema:** remove interface from deployment rosNetworks ([f8c2a9a](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/f8c2a9ac7bdd13587d7591feafcd9128359b472e))
* **manifests:** fix manifests of resources ([4f5e9bb](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/4f5e9bbd993c1c44d2870ac55cda8bdd6d56ca9a))
* **network:** fix network commands ([7f06c67](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/7f06c67b3dedd68ba28374489732451df0e3fc86))
* **networks:** delete in use network ([a9d2c49](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/a9d2c499bb90bcfd4baaebb55f8e3e6cf066c5d0))
* **networks:** fix device network schema ([7ebabf0](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/7ebabf03c4e96195588ffa4ca3f79c02b0825f62))
* **networks:** fix network type flag ([64bc9e3](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/64bc9e3449f22f3544ef7d067eb41cb9ee3c6cb7))
* **package:** allow executable command to be string, array or null ([c97b186](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/c97b186ebc071e386c80f3176b072b0019dc2645))
* **packages:** fix package commands ([48a92c9](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/48a92c941895b673689ab2c9efd567b3c887aad3))
* **project:** fixes raised exception in find_organization_guid helper ([6ab3838](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/6ab38380dad039921a6c174a0cb0011d80572e40))
* **rosbag:** update default statuses for list functions ([54fd266](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/54fd26627294102e8f341d693714269b2d0402f8))
* **template:** validate manifests against jsonschema ([b9f9fc4](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/b9f9fc4c22d4a548e10b445315f61517ffd5b7bc))
* **v2client:** corrects status check in poll_disk ([c6e7a8b](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/c6e7a8bac1722d901348d4c354b714b3789a8b38))
* **v2client:** fix retry exceeded error code description and action ([938ed4c](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/938ed4c2077eef8cf37d5eb8f4820f2ad0b93f95))
* **v2client:** fix v2 client org header ([313c660](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/313c6600d8b69370bf717a742cf904e53eb9dda5))


### Features

* adds filter by label option in list commands ([0c2cfe8](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/0c2cfe8aed49704c374253a5f5ae26f84f3087fe))
* **apply:** init Jinja environment with filters and rio namespace ([7dc030d](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/7dc030dddbf98c10cde23a9cae137427eeea372f))
* **config:** store org short id in the cli config ([9c9a6fa](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/9c9a6fa8c292e36fbac3dc5860c03438e6fbd6d8))
* **context:** add command to view cli config ([763e712](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/763e712e067edc2b89fa091412ea5cf879204b55))
* **deployment:** execute commands on device deployments ([#345](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/345)) ([558215b](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/558215b47c7d673774d588299a4ef4ff36b62f0e))
* **deployment:** implement restart alias for rio deployment update ([a25a85b](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/a25a85b0c398b4182b89de9e679f2f142ad23d88))
* **deployment:** uses v2 deployments APIs ([bc33295](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/bc332954d2376badf4495276cac5ddee950e9626))
* **deployment:** wait until all dependecies are running ([71d4f0a](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/71d4f0acfaa6cd43b1fdc869368f58fab9c1ef20))
* **disks:** use v2 APIs for Disk operations ([3ddb694](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/3ddb694fc7c50e4c4b03da6a8e72482c0d2ed839))
* **networks:** uses v2 networks APIs ([d967d18](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/d967d18611ad4bc80e394437928ecd9b840b7dc0))
* **packages:** uses v2 packages APIs ([1048ff5](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/1048ff53dc96504676e1d2a91f4e32565880ad50))
* **scripts:** adds install script for appimages ([#354](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/354)) ([3677bc6](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/3677bc6074beee62aebf1ec6cb2d10c08d7c59c6))
* **v2client:** adds poll methods and stream deployment logs method ([af90e83](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/af90e834d5a194ae9da847c556ee3e3cb2290daa))
* **v2client:** inject X-Request-ID in headers if REQUEST_ID in env ([5ce15f1](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/5ce15f17b3aed9d34542506c4d109c23ecc9c76c))


### Performance Improvements

* **delete:** implements multi-threaded delete operation ([a50fec0](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/a50fec084f0d08ce4a95c7f04fd035032371dd6e))


### BREAKING CHANGES

* **deployment:** The rio deployment execute command no longer supports cloud deployments.

# [8.1.0](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v8.0.0...v8.1.0) (2024-08-08)


### Features

* **configtree:** support yaml format while exporting trees ([9bd00c6](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/9bd00c608506d1043130890b55ae05d8e93247c3))
* **configtree:** supports overrides when importing config from files ([734e529](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/734e529e23747dc9ad4a8da309d80815e066da48))

# [8.0.0](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v7.6.0...v8.0.0) (2024-08-02)


### Bug Fixes

* **apply:** print file name when there is a parsing error ([413ce94](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/413ce94d7a5b039753342951b04411c2bc88ab91))
* **auth:** do not save password in cli config ([08a399c](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/08a399c52874b13786d4f9114fa3ae84b98ce95c))
* **bootstrap:** handle exceptions thrown by the cli ([d703df3](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/d703df3d107c2656b1ff128d49f89769ee739860))
* **configtree:** prefix keys with '/' when importing to etcd ([#336](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/336)) ([9c74fb5](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/9c74fb54c24c2083c4c7aa72a9c33dd4fa52d764))
* **configtree:** update sentinel key when tree is imported in etcd ([#337](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/337)) ([8ea304b](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/8ea304b914e5708d2ce8cb87ac9c88de11ff7b7c))
* **deployment:** show errors in deployments list ([66f2c7f](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/66f2c7f721181df35b3d4d6102f4d74d35f9024c))
* **device:** filter uploaded files by name in name_to_request_id ([7348be2](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/7348be2a022bfea965000d147e2804e053fb5757))
* **jsonschema:** add platform as a product for virtual devices ([#338](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/338)) ([6eb50f0](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/6eb50f0ab2bfb5e169b97654a94d7c5edbe3d6a9))
* **organization:** fix organization select command ([#339](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/339)) ([7943a4a](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/7943a4afa43cb1a191664b1c460473889201ade5))
* **package:** update the imageTag regex to support semver tags ([#335](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/335)) ([6e17408](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/6e1740805365c89e3b35427e70e6ab8e94aa1ad9))
* **v2client:** set organizationguid header by default ([#330](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/330)) ([eaa1185](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/eaa118513676370fefdc3e6867094d443192dd1f))


### Features

* adds command to list explain examples ([3fc228e](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/3fc228efed5db5e79f31826bfc851339ad121182))
* **template:** sort rendered templates by file-name ([161ddfc](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/161ddfcb257caece8be40b272abbb6d1f643b165))


### BREAKING CHANGES

* **auth:** The password is no longer saved in the riocli
config.json file.

Wrike Ticket: https://www.wrike.com/open.htm?id=1162009098

# [7.6.0](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v7.5.0...v7.6.0) (2024-07-04)


### Bug Fixes

* **device:** sets device labels correctly ([#329](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/329)) ([a3ac73d](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/a3ac73d6da5f1ae6eb8d9d95b5763bb391f3e7f4))
* **device:** sets highperf label on virtual device ([#328](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/328)) ([1eb7906](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/1eb7906641d700a50e47b791a19311a6d6f7b542))
* **project:** updates subnet when vpn is already enabled ([#324](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/324)) ([e8d553b](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/e8d553bc297772b3d774245c0ab7853c886a0c18))


### Features

* **configtree:** add export command ([6f236ae](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/6f236aedbd93999f7ed12156b747e116492c8948))
* **configtree:** add support for diff ([7df605e](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/7df605ea6b04e9c3f3109d9ce45904314b32527d))
* **configtree:** add support for merge ([a1d273f](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/a1d273f5069f48d8f32ac5d0888d6ac416be2dc5))
* **configtree:** add support for milestone ([6ada3f7](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/6ada3f7189287a799e66badfa6e4fa61bb5cd93d))
* **device:** supports onboarding hwil devices via device manifest ([#323](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/323)) ([7c257f1](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/7c257f16ce1fb3a8fa9f3997a1b8c9055ac52184))
* **hwil:** implements hwil command ([#319](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/319)) ([3e24b0b](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/3e24b0b115dba39544e170ddb8c08b1e450a49de))

# [7.5.0](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v7.4.1...v7.5.0) (2024-06-12)


### Bug Fixes

* **configtree:** fix handling org-level tree revisions in statefile ([05d2a27](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/05d2a272b35c4bb0970f4f4313dae9ace6fcc125))
* **configtree:** fix revision keys command to correctly show revision keys ([0ac9988](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/0ac998830eafb82d955ae50d842521a43ef8c7f8))
* **explain:** add livenessProbe constraints in the samples ([4e34695](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/4e34695ce6778b19592ae804efb77926fba400c3))
* **package:** corrects exec command parsing ([#312](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/312)) ([1f0a271](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/1f0a2711bef9500a391f24f4f4dd091a002c6b0d))
* **secret:** corrects corresponding list functions ([#310](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/310)) ([34b5c0b](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/34b5c0b6fe8300154b69963db46e9c70cb9a4a1e))


### Features

* **device:** add support for migrating device between projects ([ad70aed](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/ad70aed93c8f08f208c26df57786707db1e19bd4))
* **project:** adds command to update project owner ([5b4340e](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/5b4340e6d734832e09d7d7f9cfb74f9729915e63))
* **utils:** extends show_selection helper ([ce1a927](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/ce1a92768ab19fd70f226d57679a7ab64867f0c7))

## [7.4.1](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v7.4.0...v7.4.1) (2024-05-16)


### Bug Fixes

* **vpn:** fix the expiry time formatting for vpn binding ([8e7fdcb](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/8e7fdcb2ac4cc4c04d6d7f1f6cec4e170bd8bc5f))

# [7.4.0](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v7.3.3...v7.4.0) (2024-05-16)


### Bug Fixes

* **configtree:** handle project-level trees correctly in commit sub-command ([6899711](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/68997116268776dd5c050df9cd950da1dc39105f))
* **configtree:** replace --project with --organization flag ([ab3e5ca](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/ab3e5cac76178d8a3f6a2a4a393a6a2849887de9))
* corrects the with_org usage ([29d4ae4](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/29d4ae41f0fa5b751e5b36cfcdf3b17e80d3d2bc))
* **secret:** corrects corresponding find functions ([#301](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/301)) ([41e287b](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/41e287b2e4247d317468ebdf9a0f40a041f1530c))


### Features

* **configtree:** add support for key-level Metadata ([5b7c1bb](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/5b7c1bbce63921a7544f436168d3556ca8a26a02))
* **configtrees:** add support for interacting with Config trees ([f979128](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/f979128136efbaab21f221cfc75561769df15286))
* **configtree:** support exporting YAML files in `import` command ([f7f145f](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/f7f145f5fb9cf81ef4941258608814da0ca01cab))
* **graph:** add support for Graphviz ([760d6c0](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/760d6c049d5dc0e152479c7d3e025c99c7d5e2af))
* **state:** implement StateFile to store intermediate state ([3302133](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/3302133be004f974f957b1202e358b6f3521c08e))
* **vpn:** add support for registering machine for Android or iOS ([c385bea](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/c385bea1c8e0d87881eee1cf4a97138be6b479b6))

## [7.3.3](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v7.3.2...v7.3.3) (2024-03-27)


### Bug Fixes

* **project:** remove erroneous check from whoami ([#295](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/295)) ([7cdae50](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/7cdae50633846b5efa29f914a2b23ed4efc241c5))

## [7.3.2](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v7.3.1...v7.3.2) (2024-03-26)


### Bug Fixes

* **project:** corrects usergroup role check in whoami command ([#291](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/291)) ([3d859a1](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/3d859a164a8dd6f9473c20e6ffe494c7e1eaa87a))

## [7.3.1](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v7.3.0...v7.3.1) (2024-03-25)


### Bug Fixes

* **auth:** saves email_id when logged in with auth_token ([#288](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/288)) ([5fb1bbe](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/5fb1bbe373b1055dc94603da7d41c346a58c1657))
* **docs:** updates sphinx version and other dependencies ([#290](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/290)) ([c6a8116](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/c6a811643cc3b1e8ae3283949fe6523255e221ba))
* **project:** sends org when fetching guid from name ([#287](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/287)) ([6eb340b](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/6eb340bebb26cf178e20cdacb7a371efa6745cd4))

# [7.3.0](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v7.2.1...v7.3.0) (2024-03-13)


### Bug Fixes

* **jsonschema:** updates ip range regex in staticroute ([264c77b](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/264c77be213bda4792c0c6582c3449824fc8e877))


### Features

* **deployment:** adds support for host subpath uid/gid/perm ([#279](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/279)) ([61bc8c5](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/61bc8c56c2fff3b76dda687cf9f6e63769a89fdb))
* **static-route:** add support for IP Whitelisting ([85010ed](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/85010ede2aa3716fb3fc98b8920fc81c1892144e))
* **static-route:** add support for updating static-route ([c2a5305](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/c2a5305f5c4e9154cbd52e5a3d83f67492ad557e))

## [7.2.1](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v7.2.0...v7.2.1) (2024-02-27)


### Bug Fixes

* **v2client:** removes list limit for static-routes ([2eef19a](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/2eef19a583c3d8f1837273abb0117fe238e0e89c))

# [7.2.0](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v7.1.0...v7.2.0) (2024-02-26)


### Bug Fixes

* **projects:** fixes the list command ([#278](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/278)) ([15a0659](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/15a06591b3c1af6f5d679b83587834e323ff5870))
* **v2client:** makes v2Client non-singleton ([1a65f45](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/1a65f45cdcc11a4bb7087f8d53bcd500c8f9d654))


### Features

* **project:** implements whoami command ([982bff2](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/982bff2641803b8d0749f2a5ec0194c4ecc998c9))

# [7.1.0](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v7.0.3...v7.1.0) (2024-02-14)


### Bug Fixes

* corrects regex for fetching resources ([1d3c75e](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/1d3c75ed6281ec2e6dcfdc3544f37e83061dd9c7))
* sets default confirmation action to 'No' ([b3348af](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/b3348afd8ced973dbbfbc2c346924d9f2a90db07))
* **v2client:** updates limits for list secrets and routes ([#270](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/270)) ([862fdfc](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/862fdfc034d7285d2abfd05197738f83ca0589c2))


### Features

* **explain:** updates examples for region support and env var inconsistency ([#273](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/273)) ([62a2828](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/62a2828950edb7240ac60f839aac694955e47158))


### Reverts

* **explain:** adds network examples for us region ([#276](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/276)) ([3593def](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/3593defbe9ba62081a8a142f51a37520e8f47ee6))

## [7.0.3](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v7.0.2...v7.0.3) (2024-02-06)


### Bug Fixes

* **jsonschema:** corrects the regex for device volume paths ([#268](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/268)) ([fd2a881](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/fd2a881a965df09d0102c6851094e0e8e946c2ea))

## [7.0.2](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v7.0.1...v7.0.2) (2024-02-02)


### Bug Fixes

* **apply:** raises error when a metadata has no name ([#266](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/266)) ([be26ff8](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/be26ff819f639e0c4103c743a99a3871de027e33))
* **deployment:** corrects the condition to fetch deployments ([ee1265d](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/ee1265db5d126929e9e86b2898040ea33efdf87b))
* **device:** corrects the condition to fetch devices ([3785f33](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/3785f33fb53e9a37c139c57cdd8bb1b807ec1e28))
* **jsonschema:** corrects the deployment component spec ([#264](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/264)) ([3f848bf](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/3f848bfc67b9e649464d5f74fef007c08c87c1b9))
* **package:** corrects the condition to fetch packages ([f056d3a](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/f056d3a6ad2d0459a318e2c32ca18bd701ce9ca6))

## [7.0.1](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v7.0.0...v7.0.1) (2024-01-31)


### Bug Fixes

* updates default service urls in api calls ([#262](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/262)) ([4ee6f43](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/4ee6f435429a538453821f169a135e8c8423cffc))

# [7.0.0](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v6.0.0...v7.0.0) (2024-01-31)


### Bug Fixes

* **apply:** adds deploymentId as an option in GUID_KEYS ([11161ef](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/11161ef835f622710f704c38761ef22ec927a12f))
* **deployment:** prints error during delete when no deployments found ([f73fea0](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/f73fea03521bf3b4d220d0ae0fbd3f85421f0f85))
* **deployment:** raises exception when package depends not found ([b5b3daf](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/b5b3daf64dbfe10911dc09eafdcd6770a24af0c7))
* **deployment:** validates config trees while creating deployment ([8d688fc](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/8d688fc8df563cbb7a8ed78846ce40ce0f6c5682))
* **device:** improves message when devices deleted successfully ([e6b1299](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/e6b1299440abeccb9a3466c50176708d2f14698d))
* **device:** prints error during delete when no devices found ([7bf2c94](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/7bf2c944bd9c03ef3d6c79c6022c00b210c2c8b8))
* **device:** speeds up listing device deployments ([e7b0ceb](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/e7b0ceb22276ab1c85352e3f1f7155da8f1d4d2e))
* **disk:** implements retries for deleting disk ([#260](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/260)) ([c635914](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/c63591476cc7c7b5841a2928ac763c5bd789d9eb))
* **disk:** sets default retries=20 for polling disk status ([35fa0f4](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/35fa0f47365babf44573507f3258ec80c36a838e))
* **jsonschema:** adds validation on disk volume mount path ([9332b45](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/9332b451ef44d19cc395b097629b60075a35bbe9))
* **jsonschema:** disallows additional properties for device volumes ([cc702a0](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/cc702a01ed77b1fa87f035ea06818ae30b3b06ee))
* **jsonschema:** disallows additional properties for runtime dependency ([324037c](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/324037c66f2ac4cfb7384a2063a7e373f89488c8))
* **jsonschema:** makes runtime required in disks ([1d81a82](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/1d81a8229836a52ef9ff047d35d5efccf87bdf57))
* **jsonschema:** makes runtime required in package and deployment ([f2e7afe](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/f2e7afe5b9d6e866806402530a940fbf97b9f2c4))
* **jsonschema:** removes default device deployment restart policy ([64967e1](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/64967e161bb9aca5e616d61a4ef71536c31399f8))
* **jsonschema:** sets min length for secrets to 3 chars ([2703147](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/270314740b85f13a8f0ba1282d0ba722e4ad249e))
* **jsonschema:** skips populating default if property not in instance ([ba7eccf](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/ba7eccfbad133e39062e41e02686d997275b44d4))
* **organization:** empties project when organization is selected non-interactively ([921e965](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/921e965dd67b7e0805e214a8b544353a392aee62))
* **package:** prints error during delete when no packages found ([81355a7](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/81355a783f652313c8d30e5045a1cdf47ba74bce))
* **parameter:** adds validation on tree names ([5870508](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/58705083d7006c14523c4d4577d099ab2a5c77de))
* **parameter:** prints info when download command has no tree name ([695875f](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/695875f89d51a564582d4193606c0db9d47caec0))
* **parameter:** prints message when there is nothing to upload ([3aa3ea5](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/3aa3ea51907a1433d5226c45ff231b3204853071))
* **parameter:** throws error when param tree not found during apply ([9a65dd3](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/9a65dd3b8ae2e58775b82e79156d09da6a92d9da))
* **project:** skips update if VPN already enabled ([51b0222](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/51b022284d107c7bcca8502e8b06e6ea7af0d6c8))
* **secret:** adds secret name length validation ([8ae5102](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/8ae51025bd9894ed2ce496d1ecdd3ae3cd9229d3))


* refactor(deployment)!: removes ssh commands ([c066477](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/c066477bc44e6bdc57dcb96590c3527d92d34ac8))
* refactor(package)!: removes create command ([38f0580](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/38f05806d89bb89dd35686d32c30c8c319434e5b))
* 🔨 refactor!: removes build from the CLI (#241) ([4a7901d](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/4a7901d3cbf57670c99b5fd323e3940d5454ae3a)), closes [#241](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/241)


### Features

* **auth:** allow environment change without trying to fetch token ([5f4a49f](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/5f4a49fb5cc6759172db58047a3105b1a7f807cc))
* **deployment:** supports deleting multiple deployments ([f7cccc3](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/f7cccc31cda7a4b8738993c57c43aa1762bf7426))
* **package:** add support for nested docker images. ([55b05c6](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/55b05c62e769486a80e253ba413351146e8aa819))
* **parameters:** apply with device name pattern ([4a5e54c](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/4a5e54c79057aef799dc82cca351380e6e0594ea))
* **parameters:** apply with device name pattern ([6f3b34a](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/6f3b34a57d2912a134e7850ffe4f4972e08406c2))
* **utils:** implements a SimpleCache class ([0d466b6](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/0d466b63c4b3aaf0f9ffce89d959bbe947636afc))
* **utils:** implements concurrent executor helper functions ([7a67be3](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/7a67be3f40a8fdefefd44f749feec72d4137a96a))


### Reverts

* skips populating default if property not in instance" ([d482223](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/d4822230f6eaea9c7e884cf0988dd8f2e249ccfe))


### BREAKING CHANGES

* The `rio deployment ssh-init` and `rio deployment ssh`
commands are no longer available.
* rio package create is no longer available. Please use
`rio apply package.yaml` for creating new packages.
* Builds are no longer supported in Rapyuta.io. Please
use Docker images for creating packages and deployments.

# [6.0.0](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v5.0.0...v6.0.0) (2023-12-28)


### Bug Fixes

* **project:** fixes project update with vpn state ([#246](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/246)) ([82709f6](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/82709f626427f8a5ce802e0755882c04d66249d7))


### Features

* **auth:** add support for AKS staging environments ([59d30e9](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/59d30e93978516ddb9e20aecada8777fbfecd706))
* **device:** adds --advertise-routes flag in the vpn command ([6cea521](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/6cea521ffb252ea60bad8f502699e159c64b762a))
* **device:** updates device delete command to delete multiple devices ([#217](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/217)) ([1a35403](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/1a354035179d9437a5838649155b4bb774236f55))
* **jsonschema:** updates features attribute in project schema ([c4cd332](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/c4cd33286ae67b73c66fbf6bfe66f9a5abac31de))
* **project:** accepts subnets while enabling vpn ([#245](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/245)) ([06bbf7f](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/06bbf7fc238f7c568a7f9377a6628dc8160549ce))


### BREAKING CHANGES

* **jsonschema:** The vpn and tracing attributes under .spec.features
have been changed from type=boolean to type=object. Enabling vpn on a
project will now require one to set .spec.features.vpn.enabled=True and
likewise for any other project feature.

# [5.0.0](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v4.2.1...v5.0.0) (2023-10-26)


### Bug Fixes

* **vpn:** avoids sudo when running as root ([47ee4eb](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/47ee4ebfe2cba757caad11ee772aea7dc4419b41))
* **vpn:** hides spinner when asked for password ([5428cf3](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/5428cf3f68a6a9705a4dda171bbcb51b3ba9d0c3))


### Features

* **device:** updates spinner in device commands ([2b64ceb](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/2b64ceb38db83a62d9c4f14082f2164d0ff01769))
* **secret:** uses v2 secret APIs ([a24ae37](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/a24ae374fc567ce25ecf4d53918aeefa2a7f90a4))


### BREAKING CHANGES

* **secret:** Secret type "Source Secret" will be deprecated and the
rio secret create command will no longer be available. The only way to
create secrets would be via manifests.

## [4.2.1](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v4.2.0...v4.2.1) (2023-09-28)


### Bug Fixes

* **usergroup:** fixes inspect when group has deleted projects ([bdbb17e](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/bdbb17ef6a559a1607fac527ace0d88998a8dfd8))

# [4.2.0](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v4.1.1...v4.2.0) (2023-09-27)


### Bug Fixes

* **organization:** highlights logged-in user in the users list ([d93d2b2](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/d93d2b263fc3d32dbe1cce21154469afe570a0b3))
* **vpn:** displays DNS name in vpn status ([baa823d](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/baa823d27705881617723390f93bf1dbbfd5a5cd))


### Features

* **organization:** adds command to invite user ([b99fb5f](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/b99fb5f51b242b75440d07f62703ea345682a60b))
* **organiztion:** adds command to remove user ([2caeefd](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/2caeefd8bf93b4672b2f23261e66ab7f211b8a1e))
* **project,usergroup:** supports extended RBAC roles ([7a84b72](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/7a84b72404e1e460a50a402fd1272dab036d9d6a))

## [4.1.1](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v4.1.0...v4.1.1) (2023-09-22)


### Bug Fixes

* **apply:** fixes the find_functor for staticroute ([2ad8a17](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/2ad8a17323ecff0c496c75ffa7e74f4783e6a478))
* **deployment:** fixes static route dependency ([117fd86](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/117fd865e2edaf72c87293f530ced44c9a3ee3c2))
* **staticroute:** sends the correct value for name when deleting route ([5685360](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/568536064c8ad493820adeb4cab7ad468553a586))

# [4.1.0](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v4.0.3...v4.1.0) (2023-09-21)


### Bug Fixes

* **explain:** corrects livenessProbe examples in packages ([69b7ad1](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/69b7ad113fc927b146c2116bdcafe0c63f714eb9))
* **jsonschema:** corrects property name in package livenessProbe definition ([30c1a83](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/30c1a83acd3b52037ad7327e375be60fb5742dab))
* **update:** removes the requirement of privileged access ([8857138](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/8857138873a265c92c43a6db5c6329ace20b2a68))
* **usergroup:** corrects the inspect output ([fc27292](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/fc272923049868cb0164f1300b7bca38d6950fb7))
* **usergroup:** outputs a rio manifest construct in inspect ([4c32573](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/4c3257331b7559ca396ec5a28b3b11b543a36d59))


### Features

* **deployment:** adds support for paramsync in device deployments ([e5cf0ff](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/e5cf0ff36bdce897a94f052a9ce2b0dcbe327ff7))
* **organization:** adds inspect command to check org details ([232fb11](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/232fb114ceaee7864fb7a99320376c095643e059))
* **package:** adds liveness probe for device executables ([4716f72](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/4716f72fdc8f7d87d85d6c9c526fca553e08aa88))
* **static_route:** uses v2 static route APIs ([17661c3](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/17661c3b2b086f3d926857cd1fdc6952d7be5690))

## [4.0.3](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v4.0.2...v4.0.3) (2023-08-10)


### Bug Fixes

* **charts:** adds retry_count and retry_interval while applying charts ([aa025f3](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/aa025f3af26726db2a350cd1418a78bb7d559c6e))

## [4.0.2](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v4.0.1...v4.0.2) (2023-08-09)


### Bug Fixes

* **apply:** reads files within nested directories ([85611dc](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/85611dc154c8ce9c0af1489705501254b7bf31ef))
* **apply:** returns exit code when apply command fails ([d77bb5e](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/d77bb5e81662880640d4ff0a567fd650f1868025))
* **device:** fixes error handling when deleting a device ([de7289c](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/de7289c11a8894e2f2fe510d240e901125b78c02))

## [4.0.1](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v4.0.0...v4.0.1) (2023-08-07)


### Bug Fixes

* implements dummy spinner for non-tty environments ([140e65f](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/140e65f13dfe3b4a0be5c69f5799a5cb93697e23))
* **network:** corrects the message on successful deletion ([0b3acd2](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/0b3acd2d12750a0d770976510616037df2a3750c))
* **utils:** fixes type annotation issue with Python 3.7 and 3.8 ([1ed0506](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/1ed0506a269bc1432b20b10def2d7c3ee132f47a))

# [4.0.0](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v3.1.0...v4.0.0) (2023-08-03)


### Bug Fixes

* **apply:** corrects the guid_functor for network ([347e430](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/347e4306ff6b73204da66dc81fe046a8195e8a43))
* **deployment:** handles error in name_to_guid ([47b5f8f](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/47b5f8fb8073273691d0fd6bc25b15ccbda79f4c))
* **deployment:** sets dependent deployment ready phase to PROVISIONING ([1444186](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/14441863dc723dd810a57a48a9ad793c257898c2))
* **jsonschema:** adds regex pattern to usergroup schema ([9235863](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/923586372f630fad68b32c70d26eedbd45af1a49))
* **jsonschema:** updates the projectGUID regex pattern ([63b975e](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/63b975e11386cda7aaea95d083a7f898e0f971fd))
* **network:** handles error in name_to_guid ([2f73774](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/2f737742de27697cdefee755ee684cd3b225945e))
* **organization:** fixes KeyError in organization users command ([6b3c867](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/6b3c86771ef999266d99bc8bcb585034b3bc440b))
* **parameter:** fixes nested directory diff ([7445972](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/74459724fe6fa2c1ac36628aabfb798af185cf76))
* **usergroup:** fixes create_object method signature ([d74f539](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/d74f53960f77a7c0907fe1db05231085234900d5))
* **usergroup:** handles NoneType error in inspect command ([3b111a6](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/3b111a6d642f9c9cf8b40e19982f3ef07df71d53))
* **usergroup:** update usergroup removes active admins ([ca67437](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/ca67437d05bf878774abe46dff9ac97fc12f0de0))


### Features

* adds command to update the CLI ([c64c9d7](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/c64c9d7d82168149a5052422b426aee36417480b))
* **apply:** adds retry count and sleep interval flags ([1cdeb65](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/1cdeb65e1ad11468565a0de0aa074bd880e06c3c))
* **apply:** adds yaspin spinner to apply family of commands ([c6e0975](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/c6e09755257bf8a389f53f6572c9593c2c0f3109))
* **auth:** updates spinner and refactors existing code ([dd33d75](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/dd33d75c5b9710b6da6d372458bb97e8eda2608d))
* **chart:** adds spinner and refactors code ([ff28002](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/ff28002f8fa091a8d3834584d57a5bafabe4c894))
* **constants:** defines colors and symbols as constants ([8ad2cad](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/8ad2cad3d8ffa585349790ceb31058875278de74))
* **deployment:** adds command to update deployments ([e04e5dd](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/e04e5dd70db3da199000aae352fbf9bd413bd968))
* **deployment:** updates spinner and refactors existing code ([458b44e](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/458b44e3b78222295d2b67849e0312de278aee92))
* **device:** adds or updates spinner in device commands ([c14ebf4](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/c14ebf451cb7a6eb863e5babcba430490cb750ee))
* **disk:** list command shows used and available capacity ([0361904](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/0361904ec6d775013c8ca851d15b093bf4e0cb2c))
* **disk:** updates spinner and existing implementation ([4c080d0](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/4c080d0680ed9a24c019a4759ff23206c99039d2))
* **network:** updates spinner and refactors existing commands ([e0621dc](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/e0621dc2a1d1c6ecc1842fbe26cd1f9a749fbac3))
* **organization:** adds command to list users ([19a06f8](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/19a06f81a22adb128e4924650c023d4edeffce2a))
* **organiztion:** adds option to set project non-interactively ([3c2e848](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/3c2e8486318a473e27a28c5f3a53b70d95aaed12))
* **parameter:** adds spinner and constants ([a4f954e](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/a4f954eb706c9256de1b6ed22f55221c87e840d5))
* **project:** adds yaspin implementation to project commands ([44a5a1c](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/44a5a1ced136ae7d834a798ec19ac206c5e07ea1))
* **secret:** updates spinner and refactors existing commands ([0949154](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/09491549a6bfccc3ad3979138e252d663e408a85))
* **static-route:** updates spinner and other implementations ([7184016](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/7184016bd4edb05959eadcaea30f198ce3cde7a8))
* **usergroup:** adds usergroup command ([c57891e](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/c57891ef9d8bb32bed3582188061bcd4ec21cdee))
* **vpn:** adds spinner and refactors implementation ([#188](https://github.com/rapyuta-robotics/rapyuta-io-cli/issues/188)) ([0af180f](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/0af180fb8db7e60eeefd62f4eea57aab7f3bba3d))


### Performance Improvements

* **deployment:** poll deployment till provisioning phase ([ea72999](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/ea729995e9ebe15c99757d0f22a5ec2a4ef16dc5))


### BREAKING CHANGES

* **deployment:** Deployment will be polled till provisioning

# [3.1.0](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v3.0.0...v3.1.0) (2023-06-14)


### Bug Fixes

* **explain:** adds missing sections in deployment examples ([1a8d207](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/1a8d207dabd66c809c5c48ee5240c6294ec3cc0b))
* **package:** validates maximum cpu limit for device executables ([ba78470](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/ba7847084df5946efff8d1c4871623fe291a3825))
* removes `create` option for specific resources. ([0d1dd8f](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/0d1dd8fb6ccede41638d1324dedd5df771a47d75))
* removes import option from build and secret ([98ea4d0](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/98ea4d0e2ae655eb3f9459c53448dc7b6bdda639))


### Features

* **apply:** adds option show dependency graph ([70f8950](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/70f8950375e669d297143c7f696d886e4fb6cbe3))
* **auth:** allows login with just an auth token ([fcadc33](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/fcadc33ceab14fb782bd1d3f05d63f35e6c5bcb6))
* **auth:** allows selecting token level ([e8dc9b6](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/e8dc9b6b13a58bf3399f02f7dcc424785e408330))
* **deployment:** adds the option to execute commands on cloud deployment containers ([7ec3fb1](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/7ec3fb1e727d16c21760ded0e0321d5ac837d2cc))
* **package:** adds provision to specify pull policy for docker image ([42ca473](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/42ca473bbe598d18a6b0ae0addc9feca26a39531))
* **package:** supports resource limits on device runtime ([b5ec154](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/b5ec15484c0e677ed56082033707b277b4fddb23))

# [3.0.0](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v2.0.2...v3.0.0) (2023-05-17)


### Bug Fixes

* **deployment:** added device error code descriptions and actions ([af2ecb7](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/af2ecb7cfd5a1bb688156b1f4f66f55a609eb407))
* **deployment:** fixes inspect command when some fields are null ([a80f2e6](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/a80f2e6d1caa85dfb5d7304bcee3276541a09cc0))
* **device:** fixes delete command ([f2599e5](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/f2599e524da36175fd6257f1d214cad875bd53fa))
* **explain:** verbose examples for explain command ([c5dcf8a](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/c5dcf8ac0b252bb47a06a40334c342451d5a7c09))
* **jsonschema:** sets default values defined in the schema ([76b403a](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/76b403a47c262ff3b7137fc81b82a8eb4a25493b))
* **project:** improves error reporting on server errors ([fec2fcb](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/fec2fcb0af83d01b5d8a24e23fc9138cb022e929))
* **v2client:** handles 5xx server errors ([b7cf0cf](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/b7cf0cf97bb197036dbc615f4dfb42d3ac1e17ed))


### Features

* **deployment:** adds toggle to enable cloud params ([9cc7981](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/9cc79816f398dc382960df5edca1a3364167ea22))
* **deployment:** adds vpn client toggle in manifest ([a6223cc](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/a6223cc8b65b897647b1673be1336d30c8010459))
* **device:** add command to toggle vpn client on device ([6feaa20](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/6feaa20a61d8f640f8e29e6c320c134ebe8d01f4))
* **managedservice:** adds command to delete instance ([5761c25](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/5761c25c6740666addf5132cda3aec4cb58eb9d3))
* **organization:** adds organization command in the CLI ([5a5f599](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/5a5f599de18ed4135361f833514da8b6ac29746d))
* **project:** adds project features sub-command ([981dc3a](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/981dc3afd0670e61976651e6177d85269085b01a))
* **project:** uses v2 project APIs and schema ([d1290aa](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/d1290aa1bd4c3f0c11d419dac68f5829fd8efcad))
* **project:** waits for project to succeed during apply ([adb004b](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/adb004bc7c106bfed26441aa65fea6c3db43f124))
* sets --silent as an option alongside --force ([b5ca2b4](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/b5ca2b485fdd04acf7eef841793f4e1b6ffb015f))
* **shell:** adds org name in shell prompt ([3edfd5e](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/3edfd5e8646a6f1623e3f70c3f1b0e30894c4eab))
* **vpn:** adds vpn connectivity support ([b01605c](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/b01605c0f007a67c8c26e7bac0bbb4f813e790e6))


### BREAKING CHANGES

* **organization:** This commit modifies the login command options.
Commands with the following structure will break

rio auth login --email <> --password <> --project <> --no-interactive
* **project:** This commit updates the project schema. Existing
manifests may not work.

## [2.0.2](https://github.com/rapyuta-robotics/rapyuta-io-cli/compare/v2.0.1...v2.0.2) (2023-04-20)


### Bug Fixes

* **apply:** fixes the schema not found errors ([d4847a5](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/d4847a53c7b103e8d4400f5c815ea6e5cb5b60f6))
* **network:** adds _get_limits method for cloud routed network. ([4751307](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/4751307e53f554904184527271b4ba133a5e7d73))
* **parameter:** handles the non-directory tree names ([bbf65f2](https://github.com/rapyuta-robotics/rapyuta-io-cli/commit/bbf65f22585925241d4a99179025e2ef09c55af1))

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
