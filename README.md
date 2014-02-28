简介
====
devman 这个项目源自某团队内部项目管理系统，可以满足中型甚至大型项目的 git svn 代码树管理，项目 wiki 策划、文档编写，bug 跟踪解决管理，测试用例管理等。 因为其中有几个非常有意思的模块，所以特意裁剪，编写相应文档，以开源模式给予大家构建项目时做参考。

其主要模块包括：
-------------------
* svn 仓库和 git 仓库管理。
* apache ssl 访问权限控制模块，用来控制 trac 的访问权限。
* ssh 远程访问权限控制模块 (插入 pam 模块)，用来控制代码树的访问权限。
* 支持通过 SSO 和本地账号登录。可以通过 SSO 同步用户账户密码，并在本地维护一套类似于 unix 系统的 group 概念管理权限。
* 提供一个网站后台 (django 搭建) 添加删除修改用户和用户权限。
* 与 python 的 trac 绑定，提供项目的 wiki 和 bug 管理。

安装说明见：
-------------------
http://www.hackos.org/wiki/index.php/Devman_UserGuide

WIKI Index
-------------------
http://www.hackos.org/wiki/index.php/Devman
