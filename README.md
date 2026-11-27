# 圣诞盲盒 · 视频数据包

两个数据集，都已打好包放在 GitHub Release，附礼物/场景分类目录。

| 数据集 | 来源 | 记录 | 视频 | 大小 | Release |
|---|---|---|---|---|---|
| 第一波（完整） | 人工标注页 `ALL_DATA`（178 case） | 178 | 178 目标成片 + 40 候选 | 2.33 GB / 2 卷 | [v3](../../releases/tag/v3) |
| 第二波（训练集） | `AMU：训练集-圣诞盲盒真实数据第二波.xlsx` | 430 | 407 目标成片 | 4.12 GB / 3 卷 | [v2](../../releases/tag/v2) |

覆盖：两波合起来用到了礼物目录里全部 **100 个盲盒**（第一波 82 个，第二波 99 个，重叠 81 个）。

## 国内直链（推荐，实测 25 MB/s）

阿里云 OSS 公开读，前缀 `xmas-blindbox/`，总览页：
<https://tianjiu-cockpit.oss-cn-hangzhou.aliyuncs.com/xmas-blindbox/index.html>

```bash
BASE=https://tianjiu-cockpit.oss-cn-hangzhou.aliyuncs.com/xmas-blindbox
mkdir -p xmas && cd xmas
for f in wave1/wave1_part01.zip wave1/wave1_part02.zip \
         wave2/wave2_part01.zip wave2/wave2_part02.zip wave2/wave2_part03.zip; do
  curl -L -C - -O "$BASE/$f" --create-dirs
done
for z in wave1/*.zip wave2/*.zip; do unzip -o "$z" -d "${z%%/*}"; done
```

## GitHub 备份（海外快、国内慢，实测 34 KB/s）

第一波：

```bash
curl -sL -H "Accept: application/vnd.github.raw" \
  https://api.github.com/repos/Renjie-hub-byte/xmas-blindbox-videos/contents/wave1/fetch.py \
  | python3 -
cd wave1 && for z in wave1_part*.zip; do unzip -o "$z"; done
```

第二波：

```bash
curl -sL -H "Accept: application/vnd.github.raw" \
  https://api.github.com/repos/Renjie-hub-byte/xmas-blindbox-videos/contents/wave2/fetch.py \
  | python3 -
cd wave2 && for z in wave2_part*.zip; do unzip -o "$z"; done
```

## 分类目录（catalog）

| 文件 | 内容 |
|---|---|
| `catalog/gifts.csv` | 100 个盲盒：`gift_id`(Bxx-Cyy)、礼物大类（车/游艇/私人飞机/豪宅/手表/包包/吉他/音响/雪服/旅行地）、普通款/隐藏款、品牌英文名、图片链接 |
| `catalog/scenes.csv` | 40 个源视频候选：A 组 10 个场景、B 组 10 个礼物大类的 v1/v2（性别不同），含中英文名、评估集 ID、预览与原片地址 |
| `manifests/wave1_manifest.csv` | 第一波 178 行 × 全部字段（含礼物大类、品牌、场景名、所属分卷），已并入 catalog 列 |
| `manifests/wave2_manifest.csv` | 第二波 430 行 × Excel 原字段 + 礼物大类、品牌、场景名、所属分卷 |

这两个 manifest 也以同名校验版放在各自 release 里（`wave1_manifest_enriched.csv` / `wave2_manifest_enriched.csv`），内容一致。

## 目录结构

第一波（v3）：

```
videos/wave1/H3/B07/000_B07-C10_target.mp4     # 模型 / 礼品组Bxx / idx_礼品ID
videos/wave1/Kling4.0/B10/177_B10-C02_target.mp4
videos/wave1/candidates/A_a05_v1_female.mov    # 40 个候选，多个 case 共用
```

第二波（v2）：

```
videos/H3/external/r002_tpl_xxx.mp4             # 模型 / 内部or外部 / Excel行号_tpl
videos/Kling4.0/internal/...
```

## 早期 v1（已作废）

[v1](../../releases/tag/v1) 是第一波前 23 个 case 的临时包（当时页面数据被截断），已被 v3 完整替代，不要再用。