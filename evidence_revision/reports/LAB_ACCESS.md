# 实验室连接检查

用户提供：111.2.199.31:8353，用户名wangjingjing；SSH协议尚待确认。

当前云环境没有 ~/.ssh 目录、SSH agent、已注入SSH身份或已配置主机。VPN未配置，TCP grants为空。运行时官方TCP路径仅支持经VPN且有grant的私网/CGNAT目的地址；该公网IPv4不在支持范围。没有尝试绕过代理直接SSH，故尚未测到服务器认证阶段，不能声称服务器拒绝密码或账号不可用。

用户可在自己电脑PowerShell/终端执行：

```sh
ssh -p 8353 wangjingjing@111.2.199.31
```

首次主机指纹应向服务器管理员确认后接受。若要求密码，该账号可能由管理员预设密码，或要求公钥认证；“自己没设置密码”不表示账号无密码。不要在聊天发送密码或私钥。把成功/超时/Permission denied等非秘密结果告知即可。

登录成功后仅做只读检查：

```sh
nvidia-smi
python3 -c 'import torch; print(torch.__version__); print(torch.cuda.is_available())'
```

下一步需要管理员确认SSH端口、认证方式、已有模型目录、允许使用的GPU时段。当前云会话若无法支持到公网SSH的网络路径，可在实验室机器运行已交付的gpu_eval.py，或由实验室提供受认证的HTTPS推理服务（服务域名需环境访问许可）；不把SSH密码当HTTPS代理secret，不自动安装VPN或暴露无认证服务。

用户要求自行尝试后，实际通过受支持TCP路径对proxy:8088发起有10秒超时的连接，准备CONNECT到111.2.199.31:8353。结果在连接proxy:8088时返回ConnectionRefusedError [Errno111] Connection refused，尚未发送到目标SSH服务器，也未进入账号认证阶段。此结果说明当前TCP代理入口不可用，不能解释为实验室服务器拒绝连接或密码错误。未尝试绕过代理直连。
