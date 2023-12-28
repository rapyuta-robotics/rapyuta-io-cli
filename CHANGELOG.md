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
