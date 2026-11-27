# 圣诞盲盒标注视频包

22 个 case 的视频素材，共 50 个不重复文件：

| 类型 | 数量 | 说明 |
|---|---|---|
| `videos/targets/` | 22 | 每个 case 的目标成片（带 invisible watermark） |
| `videos/candidates/` | 28 | A/B 组源视频候选，按 `组_id_版本_性别` 命名 |

- `manifest.csv`：22 个 case 与各自 1 个 target + 4 个候选视频的对应关系（A_v1 / A_v2 / B_v1 / B_v2）
- `videos.csv`：每个文件的原下载地址、场景名等元数据

## 下载

```bash
curl -L -o xmas-blindbox-videos.zip \
  https://github.com/Renjie-hub-byte/xmas-blindbox-videos/releases/download/v1/xmas-blindbox-videos.zip
```

解压后目录结构：

```
videos/targets/00_B07-C10.mp4
videos/candidates/A_a07_v1_female.mov
...
manifest.csv
videos.csv
```
