# Renaissance Dumper

A simple images & scripts dumper for [Renaissance](https://vndb.org/v611).

[Renaissance](https://vndb.org/v611) 的图像和剧本解包工具。

## Usage / 使用方法

```bash
pip install -r requirements.txt
python ebp_dump.py /path/to/ebp.fga  # For ebp.fga
python srp_dump.py /path/to/srp.fga  # For srp.fga
```

### Packer

- 粗糙且性能低下的代码，仅仅只是 PoC，完成了验证工作；
- `.EBP.bmp` 的打包并没有实际压缩文件，文件会更大一些；
- 您需要自己想办法让游戏支持中文编码。

需要被打包的图像必须以 `.EBP.bmp` 结尾：

```bash
python ebp_pack.py /path/to/ebp/folder
```

需要被打包的剧本必须以 `.SRP.txt` 结尾：

```bash
python srp_pack.py /path/to/srp/folder
```
