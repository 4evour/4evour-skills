# Git 提交身份与上传检查

本仓库维护者使用 `4evour <167200760+4evour@users.noreply.github.com>`。GitHub 登录账号负责上传权限，Git 的 `user.name` / `user.email` 负责写入提交；两者需要分别配置。每个提交同时包含作者和提交者，单独使用 `--author` 不能修正提交者。

## 当前电脑或新克隆目录

在 Windows PowerShell 中运行：

```powershell
.\scripts\setup-git-identity.ps1
git var GIT_AUTHOR_IDENT
git var GIT_COMMITTER_IDENT
```

脚本在当前仓库写入身份，开启 `user.useConfigOnly`，并将 `core.hooksPath` 设为 `.githooks`。配置只在本机生效，新克隆目录需重新运行。其他贡献者可使用 `-Name` 和 `-Email` 设置自己的身份。脚本遇到现有的其他钩子目录会停止，需先整合检查。

`pre-commit` 检查实际作者和提交者，包括环境变量覆盖；`pre-push` 检查每个分支本次新增的所有提交，防止其他工具生成的错误身份提交被上传。检查只针对新增提交，保留远端既有作者及历史修复。若缺少远端基准对象，先获取远端更新；身份错误时修正配置和待上传提交，再正常推送。

## 在同一电脑区分个人与公司仓库

Git 支持按远端地址条件加载配置。在全局 Git 配置末尾添加指向个人配置的条件，可让新的个人仓库选用正确身份：

```gitconfig
[includeIf "hasconfig:remote.*.url:https://github.com/4evour/**"]
    path = ~/.gitconfig-4evour
[includeIf "hasconfig:remote.*.url:git@github.com:4evour/**"]
    path = ~/.gitconfig-4evour
[includeIf "hasconfig:remote.*.url:ssh://git@github.com/4evour/**"]
    path = ~/.gitconfig-4evour
```

对应 `~/.gitconfig-4evour` 内容为：

```gitconfig
[user]
    name = 4evour
    email = 167200760+4evour@users.noreply.github.com
    useConfigOnly = true
```

仓库级配置优先；环境变量仍可能覆盖作者或提交者，因此还需安装钩子。使用其他主机别名或未匹配的远端地址时，应显式运行安装脚本。

## 验证

```powershell
python -m unittest discover -s scripts/tests -v
git config --show-origin --get-regexp '^(user\.|identity\.|core\.hooksPath)'
git log origin/main..HEAD --format='%h | %an <%ae> | %cn <%ce>'
git push origin main
```

测试会在临时仓库验证正常提交、环境变量覆盖、错误作者和提交者、已有历史、新分支及删除引用，不改动真实仓库历史。
