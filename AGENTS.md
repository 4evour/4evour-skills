# 仓库协作约定

## Git 提交身份

- 本仓库维护者使用 `4evour <167200760+4evour@users.noreply.github.com>`，作者与提交者都必须正确，不能继承系统用户名或其他项目的公司邮箱。
- 首次提交前运行 `./scripts/setup-git-identity.ps1`，安装仓库级身份和 `.githooks/` 校验；其他贡献者可通过脚本参数设置自己的身份。
- 提交前检查 `git var GIT_AUTHOR_IDENT` 和 `git var GIT_COMMITTER_IDENT`；`--author` 只修改作者，不能用于修复提交者。
- 推送前检查所有待上传提交的作者及提交者，保留远端已有的历史修复，禁止为解决身份问题直接覆盖远端历史。
- 不跳过身份钩子；需要调整身份时更新配置并重新验证。不要提交本地凭据、Git 配置、字体二进制、生成结果或本机底图库。
- 应用目录中的开发与验收细则见各自的 `AGENTS.md`。
