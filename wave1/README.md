# 圣诞盲盒真实数据第一波 · 完整包

来源：`source_page.html`（人工标注页，178 个 case 全部内嵌在 `ALL_DATA` 里）

## 数量

| 项目 | 数量 |
|---|---|
| case | 178 |
| 目标成片（target） | 178 |
| 源视频候选（A/B 组去重后） | 40 |
| 其中也出现在第二波 Excel 的 case | 40（视频 URL 完全一致，`manifest.csv` 的 `excel_row` 列标了行号） |
| 覆盖礼物 | 82 / 100（礼物大类 10 个全覆盖） |

## 目录

```
videos/wave1/
  H3/B07/000_B07-C10_target.mp4          # 模型 → 礼品组(B01..B10) → idx_礼品ID
  Kling4.0/B10/177_B10-C02_target.mp4
  candidates/A_a05_v1_female.mov         # 40 个候选，被多个 case 共用
manifest.csv
candidates.csv
missing.csv
source_page.html
```

- `idx` 是标注页里的 case 序号（000–177），和 `manifest.csv`、页面顺序一致
- `manifest.csv` 每个 case 一行：`gift_id / gift_name / model / pick_a / pick_b / pick_c`、目标成片路径、4 个候选路径（`cand_A_v1 / A_v2 / B_v1 / B_v2`）、所在分卷、以及第二波 Excel 对应行号
- `candidates.csv` 候选视频的原地址与分组（A/B、id、v1/v2、性别）
- 礼物分类（大类 / 普通款·隐藏款 / 品牌英文名）见同 release 的 `gifts.csv`，按 `gift_id` join
- 场景中英文名见同 release 的 `scenes.csv`，按 `A_a05_v1` 这样的 key join
- release 里还有 `wave1_manifest_enriched.csv`，已把上面两表的列并进 manifest

## 下载

一条命令（不需要 gh）：

```bash
curl -sL -H "Accept: application/vnd.github.raw" \
  https://api.github.com/repos/Renjie-hub-byte/xmas-blindbox-videos/contents/wave1/fetch.py \
  | python3 -
cd wave1 && for z in wave1_part*.zip; do unzip -o "$z"; done
```

分卷是因为 GitHub 单个 release 文件上限 2GB，全部解压到同一目录会自动合并成上面的结构。