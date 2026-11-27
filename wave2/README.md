# 圣诞盲盒真实数据第二波 · 训练集视频包

来源：`source/AMU：训练集-圣诞盲盒真实数据第二波.xlsx`（430 条记录）

## 数量

| 项目 | 数量 |
|---|---|
| Excel 记录 | 430 |
| 有视频并成功下载 | 407 |
| 缺视频 | 23 |

缺的 23 条见 `missing.csv`：22 条 Excel 里 `video_url` 为空（`pay_ok=0 / billing_status=4`，未支付成功），另有 1 条异常：Excel 第 431 行（内部账号、Kling4.0、`pay_ok=1`）也没有 `video_url`。

## 目录与命名

```
videos/
  H3/
    external/r002_tpl_xxxxxxxx.mp4
    internal/r039_tpl_xxxxxxxx.mp4
  Kling4.0/
    external/...
    internal/...
manifest.csv
missing.csv
source/AMU：训练集-圣诞盲盒真实数据第二波.xlsx
```

- 一级分类：Excel G 列模型（`H3` / `Kling4.0`）
- 二级分类：Excel E 列 `is_internal`（`internal` / `external`）
- 文件名前缀 `rNNN`：Excel 行号（表头是第 1 行，数据从第 2 行开始），`r002` 就是 Excel 第 2 行
- 文件名里的 `tpl_...`：Excel A 列（表头写的是 `session_id`，实际是 template id）

## 与 Excel 对应

`manifest.csv` 按 Excel 行顺序逐行对应，包含：

- `excel_row`：Excel 行号，和文件名前缀一致
- Excel 原始列：`session_id`、`template_id`、`template_record_id`、`uid`、`is_internal`、`create_time`、`pay_ok`、`billing_status`
- 从 `agent_request_json` 拆出的：`pick_a`、`pick_b`、`pick_c`、`pick_model`、`person_1`
- `model`：Excel G 列（表头写 `pay_point`，内容实际是模型名）
- `file`：压缩包内相对路径
- `status`：`ok` / `missing_video_url` / `download_failed`
- `part`：该文件在哪个分卷 zip 里
- release 里另有 `wave2_manifest_enriched.csv`：把 `pick_c` 解析成 `gift_id`（Bxx-Cyy），并并入礼物大类、普通款/隐藏款、品牌英文名、A/B 场景中英文名

用 Excel 的 A 列 `tpl_...` 或行号，都能在 `manifest.csv` 里查到对应视频文件。

## 分卷

GitHub 单个 release 文件上限 2GB，所以视频按累计大小切成多个 `wave2_partNN.zip`（每个约 1.3GB）。全部解压到同一目录即可合并成上面的结构。

一条命令（不需要 gh）：

```bash
curl -sL -H "Accept: application/vnd.github.raw" \
  https://api.github.com/repos/Renjie-hub-byte/xmas-blindbox-videos/contents/wave2/fetch.py \
  | python3 -
cd wave2 && for z in wave2_part*.zip; do unzip -o "$z"; done
```

或已安装 gh：

```bash
gh release download v2 -R Renjie-hub-byte/xmas-blindbox-videos -D wave2 -p 'wave2_part*.zip'
cd wave2 && for z in wave2_part*.zip; do unzip -o "$z"; done
```
