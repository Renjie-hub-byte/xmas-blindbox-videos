# 圣诞盲盒标注视频包

22 个完整 case + 1 个残缺 case（只有目标成片），共 51 个不重复文件：

| 目录 | 数量 | 说明 |
|---|---|---|
| `videos/targets/` | 23 | 每个 case 的目标成片（带 invisible watermark） |
| `videos/candidates/` | 28 | A/B 组源视频候选，按 `组_id_版本_性别` 命名 |

- `manifest.csv`：case 与各自 target + 4 个候选视频的对应关系（A_v1 / A_v2 / B_v1 / B_v2）
- `videos.csv`：每个文件的原下载地址、场景名等元数据

## 下载

海外直链：

```bash
curl -L -o xmas-blindbox-videos.zip \
  https://github.com/Renjie-hub-byte/xmas-blindbox-videos/releases/download/v1/xmas-blindbox-videos.zip
```

国内网络（GitHub API，AI 可直接拉取）：

```bash
curl -L -H "Accept: application/octet-stream" \
  -o xmas-blindbox-videos.zip \
  https://api.github.com/repos/Renjie-hub-byte/xmas-blindbox-videos/releases/assets/800744069
```

校验：

```bash
shasum -a 256 xmas-blindbox-videos.zip
# ac02050ccddfe1bfaea084227753c751839a3d0b4568e38670efd09413ae8b75
```

解压后目录结构：

```
videos/targets/00_B07-C10.mp4
videos/candidates/A_a07_v1_female.mov
...
manifest.csv
videos.csv
```

## 第二波训练集（v2）

430 行 Excel，407 个视频，4.1GB，按 GitHub 2GB/文件限制切成 3 个分卷：

```bash
curl -sL -H "Accept: application/vnd.github.raw" \
  https://api.github.com/repos/Renjie-hub-byte/xmas-blindbox-videos/contents/wave2/fetch.py \
  | python3 -
cd wave2 && for z in wave2_part*.zip; do unzip -o "$z"; done
```

目录按 `videos/{H3,Kling4.0}/{internal,external}/rNNN_tpl_xxx.mp4` 组织，`rNNN` 是 Excel 行号。
详细说明见 [wave2/README.md](wave2/README.md)。
