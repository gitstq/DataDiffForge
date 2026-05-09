<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/Tests-182%20Passed-brightgreen.svg" alt="182 Tests Passed">
  <img src="https://img.shields.io/badge/Dependencies-Zero-success.svg" alt="Zero Dependencies">
  <img src="https://img.shields.io/badge/Version-1.0.0-orange.svg" alt="v1.0.0">
</p>

<h1 align="center">🔍 DataDiffForge</h1>

<p align="center">
  <strong>Lightweight Structured Data Diff & Intelligent Merge Engine CLI</strong><br>
  轻量级结构化数据差异比对与智能合并引擎
</p>

<p align="center">
  <a href="#简体中文">简体中文</a> • <a href="#繁體中文">繁體中文</a> • <a href="#english">English</a>
</p>

---

<a id="简体中文"></a>

## 🇨🇳 简体中文

### 🎉 项目介绍

**DataDiffForge** 是一款专为开发者打造的轻量级结构化数据差异比对与智能合并命令行工具。

在日常开发中，我们经常需要对比两份配置文件的差异、合并不同环境的配置、追踪 API 响应的变化、或者在团队协作中解决配置冲突。传统的文本 diff 工具（如 `git diff`）只能逐行比较文本，无法理解 JSON、YAML、TOML 等结构化数据的语义——一个键值的位置变化就会被误报为"删除+新增"，而非"修改"。

**DataDiffForge 正是为了解决这个痛点而生。** 它能够深度理解数据的嵌套结构，精准定位每一个变更的 JSONPath 路径，并提供多种智能合并策略来自动解决冲突。

#### 💎 核心价值

- **语义级比对**：理解数据结构，而非逐行文本比较
- **零依赖安装**：纯 Python 标准库实现，`pip install` 即可使用
- **多格式支持**：JSON（支持注释）、YAML、CSV、TOML 全覆盖
- **智能合并**：4 种内置策略，支持三路合并与冲突检测
- **丰富输出**：终端彩色、JSON、HTML、Markdown 四种报告格式

#### 🔥 差异化亮点

| 特性 | DataDiffForge | 传统 diff 工具 | 配置管理工具 |
|------|:---:|:---:|:---:|
| 结构化语义理解 | ✅ | ❌ | ⚠️ 部分支持 |
| 零外部依赖 | ✅ | ✅ | ❌ |
| 多格式支持 | ✅ | ⚠️ | ⚠️ |
| 智能合并策略 | ✅ | ❌ | ⚠️ |
| 三路合并 | ✅ | ✅ | ⚠️ |
| HTML 可视化报告 | ✅ | ❌ | ⚠️ |
| 快照管理 | ✅ | ❌ | ⚠️ |
| 文件监听模式 | ✅ | ❌ | ❌ |

---

### ✨ 核心特性

- 🔍 **深度递归比对** — 支持任意嵌套层级的字典、列表和基本类型比较，精准定位每一处变更
- 📍 **JSONPath 追踪** — 每个变更都附带完整的 JSONPath 路径（如 `$.users[0].name`），一目了然
- 🧠 **智能合并引擎** — 内置 4 种合并策略：保留两者、左优先、右优先、智能合并
- 🔀 **三路合并** — 支持基于基准文件的三路合并，自动检测双方修改冲突
- 📄 **多格式解析** — 原生支持 JSON（含注释剥离）、YAML、CSV、TOML 四种结构化数据格式
- 🎨 **彩色终端输出** — 终端报告使用 ANSI 颜色编码，绿色新增、红色删除、黄色修改、紫色类型变更
- 🌐 **HTML 可视化报告** — 生成自包含的 HTML 报告，内联 CSS，可直接在浏览器中查看
- 📊 **JSON 结构化输出** — 输出机器可读的 JSON 格式，方便集成到 CI/CD 流水线
- 📝 **Markdown 报告** — 生成 Markdown 表格格式的差异报告，适合存入文档或 PR 描述
- 📸 **快照管理** — 为数据文件创建快照，支持标签标记和时间戳，方便历史对比
- 👀 **文件监听模式** — 实时监控两个文件的变化，自动计算并展示差异
- 🚫 **路径忽略** — 支持使用 glob 模式忽略指定路径（如 `$.metadata.*`、`$.temp`）
- 📏 **深度限制** — 可设置最大比较深度，提升大文件的比对效率
- 📈 **统计摘要** — 自动生成变更统计：新增数、删除数、修改数、类型变更数、最大深度

---

### 🚀 快速开始

#### 📋 环境要求

- **Python** 3.8 或更高版本
- **操作系统**：Windows / macOS / Linux 全平台支持
- **网络**：无需网络连接（零依赖，离线可用）

#### 📦 安装方式

**方式一：从 PyPI 安装（推荐）**

```bash
pip install datadiffforge
```

**方式二：从源码安装**

```bash
git clone https://github.com/gitstq/DataDiffForge.git
cd DataDiffForge
pip install .
```

**方式三：开发模式安装**

```bash
git clone https://github.com/gitstq/DataDiffForge.git
cd DataDiffForge
pip install -e .
```

#### ⚡ 30 秒上手

```bash
# 1. 比对两个 JSON 文件
datadiff diff config.json config-new.json

# 2. 生成 HTML 差异报告
datadiff diff old.yaml new.yaml -f html -o report.html

# 3. 智能合并两个配置文件
datadiff merge base.json updated.json -s smart -o merged.json

# 4. 创建数据快照
datadiff snapshot production.json -l "v2.0-release"

# 5. 实时监听文件变化
datadiff watch local.json remote.json -n 3
```

---

### 📖 详细使用指南

#### 1️⃣ `diff` — 差异比对

比对两个结构化数据文件的所有差异。

```bash
# 基本用法
datadiff diff file1.json file2.json

# 指定输出格式
datadiff diff file1.json file2.json -f html -o diff-report.html
datadiff diff file1.json file2.json -f json -o diff-result.json
datadiff diff file1.json file2.json -f markdown -o diff-summary.md

# 忽略特定路径
datadiff diff file1.json file2.json -i "$.metadata" -i "$.timestamp"

# 限制比较深度
datadiff diff file1.json file2.json -d 3

# 仅显示统计信息
datadiff diff file1.json file2.json --stat

# 禁用彩色输出
datadiff diff file1.json file2.json --no-color
```

**输出示例：**

```
=== Diff: config.json vs config-new.json ===

  ~ $.version: "1.0.0" -> "2.0.0"
  + $.features[2]: "dark-mode"
  - $.deprecated: true
  * $.config.timeout: 30 -> "30"  (type: int -> str)
  + $.server.host: "0.0.0.0"

Summary:
  Total changes: 5
  + Added: 2
  - Removed: 1
  ~ Modified: 1
  * Type Changed: 1
  Max depth: 2
```

#### 2️⃣ `merge` — 智能合并

将两个数据文件智能合并为一个。

```bash
# 使用智能策略合并（默认）
datadiff merge left.json right.json -o merged.json

# 指定合并策略
datadiff merge left.json right.json -s left-wins -o merged.json
datadiff merge left.json right.json -s right-wins -o merged.json
datadiff merge left.json right.json -s keep-both -o merged.json

# 三路合并（基于基准文件）
datadiff merge left.json right.json -b base.json -o merged.json

# 指定输出格式
datadiff merge left.yaml right.yaml -s smart -o merged.yaml
```

**合并策略说明：**

| 策略 | 说明 | 适用场景 |
|------|------|----------|
| `smart` | 智能合并：数值取平均、字符串拼接、布尔取 AND、列表去重合并 | 通用场景（推荐） |
| `left-wins` | 左侧文件优先 | 以源配置为准 |
| `right-wins` | 右侧文件优先 | 以目标配置为准 |
| `keep-both` | 保留两者（字典合并、列表连接） | 需要保留所有信息 |

#### 3️⃣ `snapshot` — 快照管理

为数据文件创建带标签的快照。

```bash
# 创建快照（默认保存到 ./snapshots/）
datadiff snapshot production.json -l "v2.0-release"

# 指定快照保存目录
datadiff snapshot config.yaml -o /tmp/snapshots -l "before-migration"
```

#### 4️⃣ `compare-snapshots` — 快照对比

对比两个快照文件之间的差异。

```bash
# 对比两个快照
datadiff compare-snapshots snapshot-v1.json snapshot-v2.json

# 指定输出格式
datadiff compare-snapshots snap1.json snap2.json -f html -o changelog.html
```

#### 5️⃣ `watch` — 文件监听

实时监控两个文件的变化并展示差异。

```bash
# 每 2 秒检查一次（默认）
datadiff watch local.json remote.json

# 自定义检查间隔
datadiff watch config.yaml config-live.yaml -n 5
```

#### 🎯 典型使用场景

**场景一：API 响应回归测试**

```bash
# 保存 API 响应快照
curl -s https://api.example.com/users | python -m json.tool > users-v1.json
datadiff snapshot users-v1.json -l "baseline"

# 更新后再次对比
curl -s https://api.example.com/users | python -m json.tool > users-v2.json
datadiff diff users-v1.json users-v2.json -f html -o api-changes.html
```

**场景二：多环境配置合并**

```bash
# 将开发环境的新配置合并到生产环境
datadiff merge production.yaml development.yaml -s smart -o merged.yaml
```

**场景三：数据库 Schema 迁移对比**

```bash
datadiff diff schema-old.json schema-new.json -i "$.metadata" --stat
```

---

### 💡 设计思路与迭代规划

#### 🏗️ 设计理念

1. **零依赖哲学** — 仅使用 Python 标准库，确保在任何环境下都能开箱即用，不受网络和包管理器限制
2. **结构优先** — 理解数据的语义结构，而非简单的文本行比较，这是与传统 diff 工具的本质区别
3. **开发者友好** — 清晰的 CLI 接口、丰富的输出格式、完善的错误提示，让开发者专注于数据本身
4. **可扩展架构** — 解析器、报告器、合并策略均采用插件化设计，方便扩展新格式和新策略

#### 🔧 技术选型

| 组件 | 技术选择 | 原因 |
|------|----------|------|
| 语言 | Python 3.8+ | 最大的开发者受众，标准库丰富 |
| CLI 框架 | argparse | 标准库内置，零依赖 |
| YAML 解析 | 自研正则引擎 | 避免 PyYAML 依赖 |
| TOML 解析 | 自研正则引擎 | 避免 toml 依赖 |
| 测试框架 | pytest | 行业标准，生态成熟 |

#### 🗺️ 后续迭代计划

- [ ] **v1.1** — 新增 XML 格式支持、Excel (.xlsx) 格式支持
- [ ] **v1.2** — 新增交互式合并模式（TUI 界面）
- [ ] **v1.3** — 新增 diff patch 应用功能（类似 `git apply`）
- [ ] **v2.0** — 新增 Web UI 界面、团队协作功能、历史版本管理
- [ ] **v2.1** — 新增 CI/CD 集成（GitHub Actions 插件）

---

### 📦 安装与部署指南

#### pip 安装

```bash
# 从 PyPI 安装
pip install datadiffforge

# 升级到最新版
pip install --upgrade datadiffforge
```

#### 从源码安装

```bash
git clone https://github.com/gitstq/DataDiffForge.git
cd DataDiffForge
pip install .
```

#### 验证安装

```bash
# 查看版本
datadiff -v

# 查看帮助
datadiff --help

# 运行测试
pip install pytest
git clone https://github.com/gitstq/DataDiffForge.git
cd DataDiffForge
pytest tests/ -v
```

#### Docker 使用

```bash
# 构建镜像
docker build -t datadiffforge .

# 运行比对
docker run --rm -v $(pwd):/data datadiffforge diff /data/file1.json /data/file2.json
```

---

### 🤝 贡献指南

我们欢迎所有形式的贡献！无论是提交 Bug、改进文档，还是贡献新功能。

#### 📋 提交 PR 流程

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/your-feature`
3. 编写代码和测试
4. 确保所有测试通过：`pytest tests/ -v`
5. 提交代码：`git commit -m "feat: 描述你的改动"`
6. 推送分支：`git push origin feature/your-feature`
7. 创建 Pull Request

#### 📝 提交规范

遵循 Angular 提交规范：

| 类型 | 说明 |
|------|------|
| `feat:` | 新增功能 |
| `fix:` | 修复问题 |
| `docs:` | 文档更新 |
| `refactor:` | 代码重构 |
| `test:` | 测试相关 |
| `chore:` | 构建/工具链相关 |

#### 🐛 反馈问题

请通过 [GitHub Issues](https://github.com/gitstq/DataDiffForge/issues) 提交 Bug 或功能建议，提交时请附上：

- 问题描述
- 复现步骤
- 期望行为
- 实际行为
- 环境信息（Python 版本、操作系统）

---

### 📄 开源协议

本项目基于 [MIT License](https://opensource.org/licenses/MIT) 开源。

```
MIT License

Copyright (c) 2026 gitstq

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

---

<a id="繁體中文"></a>

## 🇹🇼 繁體中文

### 🎉 專案介紹

**DataDiffForge** 是一款專為開發者打造的輕量級結構化資料差異比對與智慧合併命令列工具。

在日常開發中，我們經常需要對比兩份設定檔的差異、合併不同環境的設定、追蹤 API 回應的變化，或在團隊協作中解決設定衝突。傳統的文字 diff 工具（如 `git diff`）只能逐行比較文字，無法理解 JSON、YAML、TOML 等結構化資料的語義——一個鍵值的位置變化就會被誤報為「刪除+新增」，而非「修改」。

**DataDiffForge 正是為了解決這個痛點而生。** 它能夠深度理解資料的巢狀結構，精準定位每一個變更的 JSONPath 路徑，並提供多種智慧合併策略來自動解決衝突。

#### 💎 核心價值

- **語義級比對**：理解資料結構，而非逐行文字比較
- **零依賴安裝**：純 Python 標準函式庫實作，`pip install` 即可使用
- **多格式支援**：JSON（支援註解）、YAML、CSV、TOML 全覆蓋
- **智慧合併**：4 種內建策略，支援三路合併與衝突偵測
- **豐富輸出**：終端彩色、JSON、HTML、Markdown 四種報告格式

#### 🔥 差異化亮點

| 特性 | DataDiffForge | 傳統 diff 工具 | 設定管理工具 |
|------|:---:|:---:|:---:|
| 結構化語義理解 | ✅ | ❌ | ⚠️ 部分支援 |
| 零外部依賴 | ✅ | ✅ | ❌ |
| 多格式支援 | ✅ | ⚠️ | ⚠️ |
| 智慧合併策略 | ✅ | ❌ | ⚠️ |
| 三路合併 | ✅ | ✅ | ⚠️ |
| HTML 視覺化報告 | ✅ | ❌ | ⚠️ |
| 快照管理 | ✅ | ❌ | ⚠️ |
| 檔案監聽模式 | ✅ | ❌ | ❌ |

---

### ✨ 核心特性

- 🔍 **深度遞迴比對** — 支援任意巢狀層級的字典、列表和基本型別比較，精準定位每一處變更
- 📍 **JSONPath 追蹤** — 每個變更都附帶完整的 JSONPath 路徑（如 `$.users[0].name`），一目瞭然
- 🧠 **智慧合併引擎** — 內建 4 種合併策略：保留兩者、左優先、右優先、智慧合併
- 🔀 **三路合併** — 支援基於基準檔案的三路合併，自動偵測雙方修改衝突
- 📄 **多格式解析** — 原生支援 JSON（含註解剔除）、YAML、CSV、TOML 四種結構化資料格式
- 🎨 **彩色終端輸出** — 終端報告使用 ANSI 顏色編碼，綠色新增、紅色刪除、黃色修改、紫色型別變更
- 🌐 **HTML 視覺化報告** — 產生自包含的 HTML 報告，內嵌 CSS，可直接在瀏覽器中檢視
- 📊 **JSON 結構化輸出** — 輸出機器可讀的 JSON 格式，方便整合到 CI/CD 流水線
- 📝 **Markdown 報告** — 產生 Markdown 表格格式的差異報告，適合存入文件或 PR 描述
- 📸 **快照管理** — 為資料檔案建立快照，支援標籤標記和時間戳記，方便歷史對比
- 👀 **檔案監聯模式** — 即時監控兩個檔案的變化，自動計算並展示差異
- 🚫 **路徑忽略** — 支援使用 glob 模式忽略指定路徑（如 `$.metadata.*`、`$.temp`）
- 📏 **深度限制** — 可設定最大比較深度，提升大型檔案的比對效率
- 📈 **統計摘要** — 自動產生變更統計：新增數、刪除數、修改數、型別變更數、最大深度

---

### 🚀 快速開始

#### 📋 環境需求

- **Python** 3.8 或更高版本
- **作業系統**：Windows / macOS / Linux 全平台支援
- **網路**：無需網路連線（零依賴，離線可用）

#### 📦 安裝方式

**方式一：從 PyPI 安裝（推薦）**

```bash
pip install datadiffforge
```

**方式二：從原始碼安裝**

```bash
git clone https://github.com/gitstq/DataDiffForge.git
cd DataDiffForge
pip install .
```

**方式三：開發模式安裝**

```bash
git clone https://github.com/gitstq/DataDiffForge.git
cd DataDiffForge
pip install -e .
```

#### ⚡ 30 秒上手

```bash
# 1. 比對兩個 JSON 檔案
datadiff diff config.json config-new.json

# 2. 產生 HTML 差異報告
datadiff diff old.yaml new.yaml -f html -o report.html

# 3. 智慧合併兩個設定檔
datadiff merge base.json updated.json -s smart -o merged.json

# 4. 建立資料快照
datadiff snapshot production.json -l "v2.0-release"

# 5. 即時監聽檔案變化
datadiff watch local.json remote.json -n 3
```

---

### 📖 詳細使用指南

#### 1️⃣ `diff` — 差異比對

比對兩個結構化資料檔案的所有差異。

```bash
# 基本用法
datadiff diff file1.json file2.json

# 指定輸出格式
datadiff diff file1.json file2.json -f html -o diff-report.html
datadiff diff file1.json file2.json -f json -o diff-result.json
datadiff diff file1.json file2.json -f markdown -o diff-summary.md

# 忽略特定路徑
datadiff diff file1.json file2.json -i "$.metadata" -i "$.timestamp"

# 限制比較深度
datadiff diff file1.json file2.json -d 3

# 僅顯示統計資訊
datadiff diff file1.json file2.json --stat

# 停用彩色輸出
datadiff diff file1.json file2.json --no-color
```

**輸出範例：**

```
=== Diff: config.json vs config-new.json ===

  ~ $.version: "1.0.0" -> "2.0.0"
  + $.features[2]: "dark-mode"
  - $.deprecated: true
  * $.config.timeout: 30 -> "30"  (type: int -> str)
  + $.server.host: "0.0.0.0"

Summary:
  Total changes: 5
  + Added: 2
  - Removed: 1
  ~ Modified: 1
  * Type Changed: 1
  Max depth: 2
```

#### 2️⃣ `merge` — 智慧合併

將兩個資料檔案智慧合併為一個。

```bash
# 使用智慧策略合併（預設）
datadiff merge left.json right.json -o merged.json

# 指定合併策略
datadiff merge left.json right.json -s left-wins -o merged.json
datadiff merge left.json right.json -s right-wins -o merged.json
datadiff merge left.json right.json -s keep-both -o merged.json

# 三路合併（基於基準檔案）
datadiff merge left.json right.json -b base.json -o merged.json

# 指定輸出格式
datadiff merge left.yaml right.yaml -s smart -o merged.yaml
```

**合併策略說明：**

| 策略 | 說明 | 適用場景 |
|------|------|----------|
| `smart` | 智慧合併：數值取平均、字串拼接、布林取 AND、列表去重合併 | 通用場景（推薦） |
| `left-wins` | 左側檔案優先 | 以來源設定為準 |
| `right-wins` | 右側檔案優先 | 以目標設定為準 |
| `keep-both` | 保留兩者（字典合併、列表連接） | 需要保留所有資訊 |

#### 3️⃣ `snapshot` — 快照管理

為資料檔案建立帶標籤的快照。

```bash
# 建立快照（預設儲存到 ./snapshots/）
datadiff snapshot production.json -l "v2.0-release"

# 指定快照儲存目錄
datadiff snapshot config.yaml -o /tmp/snapshots -l "before-migration"
```

#### 4️⃣ `compare-snapshots` — 快照對比

對比兩個快照檔案之間的差異。

```bash
# 對比兩個快照
datadiff compare-snapshots snapshot-v1.json snapshot-v2.json

# 指定輸出格式
datadiff compare-snapshots snap1.json snap2.json -f html -o changelog.html
```

#### 5️⃣ `watch` — 檔案監聽

即時監控兩個檔案的變化並展示差異。

```bash
# 每 2 秒檢查一次（預設）
datadiff watch local.json remote.json

# 自訂檢查間隔
datadiff watch config.yaml config-live.yaml -n 5
```

#### 🎯 典型使用場景

**場景一：API 回應回歸測試**

```bash
# 儲存 API 回應快照
curl -s https://api.example.com/users | python -m json.tool > users-v1.json
datadiff snapshot users-v1.json -l "baseline"

# 更新後再次對比
curl -s https://api.example.com/users | python -m json.tool > users-v2.json
datadiff diff users-v1.json users-v2.json -f html -o api-changes.html
```

**場景二：多環境設定合併**

```bash
# 將開發環境的新設定合併到正式環境
datadiff merge production.yaml development.yaml -s smart -o merged.yaml
```

**場景三：資料庫 Schema 遷移對比**

```bash
datadiff diff schema-old.json schema-new.json -i "$.metadata" --stat
```

---

### 💡 設計思路與迭代規劃

#### 🏗️ 設計理念

1. **零依賴哲學** — 僅使用 Python 標準函式庫，確保在任何環境下都能開箱即用，不受網路和套件管理器限制
2. **結構優先** — 理解資料的語義結構，而非簡單的文字行比較，這是與傳統 diff 工具的本質區別
3. **開發者友善** — 清晰的 CLI 介面、豐富的輸出格式、完善的錯誤提示，讓開發者專注於資料本身
4. **可擴展架構** — 解析器、報告器、合併策略均採用外掛化設計，方便擴展新格式和新策略

#### 🔧 技術選型

| 元件 | 技術選擇 | 原因 |
|------|----------|------|
| 語言 | Python 3.8+ | 最大的開發者受眾，標準函式庫豐富 |
| CLI 框架 | argparse | 標準函式庫內建，零依賴 |
| YAML 解析 | 自研正則引擎 | 避免 PyYAML 依賴 |
| TOML 解析 | 自研正則引擎 | 避免 toml 依賴 |
| 測試框架 | pytest | 業界標準，生態成熟 |

#### 🗺️ 後續迭代計畫

- [ ] **v1.1** — 新增 XML 格式支援、Excel (.xlsx) 格式支援
- [ ] **v1.2** — 新增互動式合併模式（TUI 介面）
- [ ] **v1.3** — 新增 diff patch 套用功能（類似 `git apply`）
- [ ] **v2.0** — 新增 Web UI 介面、團隊協作功能、歷史版本管理
- [ ] **v2.1** — 新增 CI/CD 整合（GitHub Actions 外掛）

---

### 📦 安裝與部署指南

#### pip 安裝

```bash
# 從 PyPI 安裝
pip install datadiffforge

# 升級到最新版
pip install --upgrade datadiffforge
```

#### 從原始碼安裝

```bash
git clone https://github.com/gitstq/DataDiffForge.git
cd DataDiffForge
pip install .
```

#### 驗證安裝

```bash
# 查看版本
datadiff -v

# 查看幫助
datadiff --help

# 執行測試
pip install pytest
git clone https://github.com/gitstq/DataDiffForge.git
cd DataDiffForge
pytest tests/ -v
```

#### Docker 使用

```bash
# 建立映像
docker build -t datadiffforge .

# 執行比對
docker run --rm -v $(pwd):/data datadiffforge diff /data/file1.json /data/file2.json
```

---

### 🤝 貢獻指南

我們歡迎所有形式的貢獻！無論是提交 Bug、改善文件，還是貢獻新功能。

#### 📋 提交 PR 流程

1. Fork 本儲存庫
2. 建立特性分支：`git checkout -b feature/your-feature`
3. 撰寫程式碼和測試
4. 確保所有測試通過：`pytest tests/ -v`
5. 提交程式碼：`git commit -m "feat: 描述你的變更"`
6. 推送分支：`git push origin feature/your-feature`
7. 建立 Pull Request

#### 📝 提交規範

遵循 Angular 提交規範：

| 類型 | 說明 |
|------|------|
| `feat:` | 新增功能 |
| `fix:` | 修復問題 |
| `docs:` | 文件更新 |
| `refactor:` | 程式碼重構 |
| `test:` | 測試相關 |
| `chore:` | 建構/工具鏈相關 |

#### 🐛 回報問題

請透過 [GitHub Issues](https://github.com/gitstq/DataDiffForge/issues) 提交 Bug 或功能建議，提交時請附上：

- 問題描述
- 重現步驟
- 期望行為
- 實際行為
- 環境資訊（Python 版本、作業系統）

---

### 📄 開源協議

本專案基於 [MIT License](https://opensource.org/licenses/MIT) 開源。

```
MIT License

Copyright (c) 2026 gitstq

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

---

<a id="english"></a>

## 🇺🇸 English

### 🎉 Introduction

**DataDiffForge** is a lightweight, zero-dependency CLI tool designed for developers who need to compare and merge structured data files with precision.

In everyday development, we frequently need to compare configuration files across environments, merge settings from different sources, track API response changes, or resolve configuration conflicts in team workflows. Traditional text-based diff tools (like `git diff`) can only compare line by line — they don't understand the semantic structure of JSON, YAML, or TOML files. A simple key reorder gets reported as "delete + add" instead of "modify."

**DataDiffForge was built to solve this exact problem.** It deeply understands nested data structures, pinpoints every change with its JSONPath, and provides intelligent merge strategies to automatically resolve conflicts.

#### 💎 Core Value

- **Semantic-level diff** — Understands data structure, not just text lines
- **Zero dependencies** — Pure Python standard library, works offline anywhere
- **Multi-format support** — JSON (with comments), YAML, CSV, TOML
- **Smart merging** — 4 built-in strategies with three-way merge and conflict detection
- **Rich output** — Colored terminal, JSON, HTML, and Markdown report formats

#### 🔥 What Sets Us Apart

| Feature | DataDiffForge | Traditional Diff | Config Mgmt Tools |
|---------|:---:|:---:|:---:|
| Structured semantic understanding | ✅ | ❌ | ⚠️ Partial |
| Zero external dependencies | ✅ | ✅ | ❌ |
| Multi-format support | ✅ | ⚠️ | ⚠️ |
| Intelligent merge strategies | ✅ | ❌ | ⚠️ |
| Three-way merge | ✅ | ✅ | ⚠️ |
| HTML visualization report | ✅ | ❌ | ⚠️ |
| Snapshot management | ✅ | ❌ | ⚠️ |
| File watch mode | ✅ | ❌ | ❌ |

---

### ✨ Core Features

- 🔍 **Deep recursive comparison** — Compares nested dicts, lists, and primitives at any depth, pinpointing every change
- 📍 **JSONPath tracking** — Every change comes with a full JSONPath (e.g., `$.users[0].name`) for easy identification
- 🧠 **Intelligent merge engine** — 4 built-in strategies: keep-both, left-wins, right-wins, smart merge
- 🔀 **Three-way merge** — Base-aware merge with automatic conflict detection when both sides modify the same key
- 📄 **Multi-format parsing** — Native support for JSON (with comment stripping), YAML, CSV, and TOML
- 🎨 **Colored terminal output** — ANSI color-coded terminal reports: green for additions, red for removals, yellow for modifications, purple for type changes
- 🌐 **HTML visualization** — Self-contained HTML reports with inline CSS, viewable directly in any browser
- 📊 **JSON structured output** — Machine-readable JSON format for CI/CD pipeline integration
- 📝 **Markdown reports** — Table-formatted diff reports, perfect for documentation or PR descriptions
- 📸 **Snapshot management** — Create labeled snapshots with timestamps for historical comparison
- 👀 **File watch mode** — Monitor two files in real-time and display differences automatically
- 🚫 **Path ignoring** — Glob-pattern support for ignoring specific paths (e.g., `$.metadata.*`, `$.temp`)
- 📏 **Depth limiting** — Set maximum comparison depth for faster processing of large files
- 📈 **Statistics summary** — Auto-generated change stats: additions, removals, modifications, type changes, max depth

---

### 🚀 Quick Start

#### 📋 Prerequisites

- **Python** 3.8 or higher
- **OS**: Windows / macOS / Linux — fully cross-platform
- **Network**: Not required (zero dependencies, works offline)

#### 📦 Installation

**Option 1: Install from PyPI (Recommended)**

```bash
pip install datadiffforge
```

**Option 2: Install from source**

```bash
git clone https://github.com/gitstq/DataDiffForge.git
cd DataDiffForge
pip install .
```

**Option 3: Development mode**

```bash
git clone https://github.com/gitstq/DataDiffForge.git
cd DataDiffForge
pip install -e .
```

#### ⚡ Up and Running in 30 Seconds

```bash
# 1. Compare two JSON files
datadiff diff config.json config-new.json

# 2. Generate an HTML diff report
datadiff diff old.yaml new.yaml -f html -o report.html

# 3. Smart-merge two config files
datadiff merge base.json updated.json -s smart -o merged.json

# 4. Create a data snapshot
datadiff snapshot production.json -l "v2.0-release"

# 5. Watch files for live changes
datadiff watch local.json remote.json -n 3
```

---

### 📖 Detailed Usage Guide

#### 1️⃣ `diff` — Compare Files

Compare all differences between two structured data files.

```bash
# Basic usage
datadiff diff file1.json file2.json

# Specify output format
datadiff diff file1.json file2.json -f html -o diff-report.html
datadiff diff file1.json file2.json -f json -o diff-result.json
datadiff diff file1.json file2.json -f markdown -o diff-summary.md

# Ignore specific paths
datadiff diff file1.json file2.json -i "$.metadata" -i "$.timestamp"

# Limit comparison depth
datadiff diff file1.json file2.json -d 3

# Statistics only
datadiff diff file1.json file2.json --stat

# Disable colored output
datadiff diff file1.json file2.json --no-color
```

**Example Output:**

```
=== Diff: config.json vs config-new.json ===

  ~ $.version: "1.0.0" -> "2.0.0"
  + $.features[2]: "dark-mode"
  - $.deprecated: true
  * $.config.timeout: 30 -> "30"  (type: int -> str)
  + $.server.host: "0.0.0.0"

Summary:
  Total changes: 5
  + Added: 2
  - Removed: 1
  ~ Modified: 1
  * Type Changed: 1
  Max depth: 2
```

#### 2️⃣ `merge` — Smart Merge

Intelligently merge two data files into one.

```bash
# Smart merge (default)
datadiff merge left.json right.json -o merged.json

# Specify merge strategy
datadiff merge left.json right.json -s left-wins -o merged.json
datadiff merge left.json right.json -s right-wins -o merged.json
datadiff merge left.json right.json -s keep-both -o merged.json

# Three-way merge (with base file)
datadiff merge left.json right.json -b base.json -o merged.json

# Specify output format
datadiff merge left.yaml right.yaml -s smart -o merged.yaml
```

**Merge Strategies:**

| Strategy | Description | Best For |
|----------|-------------|----------|
| `smart` | Numeric avg, string concat, boolean AND, list dedup merge | General use (Recommended) |
| `left-wins` | Left file takes priority | Source config is authoritative |
| `right-wins` | Right file takes priority | Target config is authoritative |
| `keep-both` | Keep both values (dict merge, list concat) | Preserve all information |

#### 3️⃣ `snapshot` — Snapshot Management

Create labeled snapshots of data files.

```bash
# Create snapshot (saved to ./snapshots/ by default)
datadiff snapshot production.json -l "v2.0-release"

# Specify output directory
datadiff snapshot config.yaml -o /tmp/snapshots -l "before-migration"
```

#### 4️⃣ `compare-snapshots` — Snapshot Comparison

Compare differences between two snapshot files.

```bash
# Compare two snapshots
datadiff compare-snapshots snapshot-v1.json snapshot-v2.json

# Specify output format
datadiff compare-snapshots snap1.json snap2.json -f html -o changelog.html
```

#### 5️⃣ `watch` — File Watch Mode

Monitor two files in real-time and display differences.

```bash
# Check every 2 seconds (default)
datadiff watch local.json remote.json

# Custom interval
datadiff watch config.yaml config-live.yaml -n 5
```

#### 🎯 Typical Use Cases

**Use Case 1: API Response Regression Testing**

```bash
# Save API response snapshot
curl -s https://api.example.com/users | python -m json.tool > users-v1.json
datadiff snapshot users-v1.json -l "baseline"

# Compare after update
curl -s https://api.example.com/users | python -m json.tool > users-v2.json
datadiff diff users-v1.json users-v2.json -f html -o api-changes.html
```

**Use Case 2: Multi-Environment Config Merge**

```bash
# Merge dev config changes into production
datadiff merge production.yaml development.yaml -s smart -o merged.yaml
```

**Use Case 3: Database Schema Migration Diff**

```bash
datadiff diff schema-old.json schema-new.json -i "$.metadata" --stat
```

---

### 💡 Design Philosophy & Roadmap

#### 🏗️ Design Principles

1. **Zero-dependency philosophy** — Built entirely on the Python standard library, ensuring it works out of the box in any environment without network access or package manager constraints
2. **Structure-first approach** — Understands the semantic structure of data, not just text lines — this is the fundamental difference from traditional diff tools
3. **Developer-friendly** — Clean CLI interface, rich output formats, and helpful error messages let developers focus on their data
4. **Extensible architecture** — Parsers, reporters, and merge strategies follow a plugin-based design for easy extension

#### 🔧 Tech Stack

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Language | Python 3.8+ | Largest developer audience, rich stdlib |
| CLI Framework | argparse | Built-in stdlib, zero dependencies |
| YAML Parser | Custom regex engine | Avoid PyYAML dependency |
| TOML Parser | Custom regex engine | Avoid toml dependency |
| Test Framework | pytest | Industry standard, mature ecosystem |

#### 🗺️ Roadmap

- [ ] **v1.1** — Add XML format support, Excel (.xlsx) format support
- [ ] **v1.2** — Interactive merge mode (TUI interface)
- [ ] **v1.3** — Diff patch apply feature (similar to `git apply`)
- [ ] **v2.0** — Web UI, team collaboration, version history management
- [ ] **v2.1** — CI/CD integration (GitHub Actions plugin)

---

### 📦 Installation & Deployment

#### pip Install

```bash
# Install from PyPI
pip install datadiffforge

# Upgrade to latest
pip install --upgrade datadiffforge
```

#### Install from Source

```bash
git clone https://github.com/gitstq/DataDiffForge.git
cd DataDiffForge
pip install .
```

#### Verify Installation

```bash
# Check version
datadiff -v

# View help
datadiff --help

# Run tests
pip install pytest
git clone https://github.com/gitstq/DataDiffForge.git
cd DataDiffForge
pytest tests/ -v
```

#### Docker Usage

```bash
# Build image
docker build -t datadiffforge .

# Run diff
docker run --rm -v $(pwd):/data datadiffforge diff /data/file1.json /data/file2.json
```

---

### 🤝 Contributing

We welcome contributions of all kinds! Whether it's reporting a bug, improving documentation, or contributing a new feature.

#### 📋 PR Submission Workflow

1. Fork this repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Write code and tests
4. Ensure all tests pass: `pytest tests/ -v`
5. Commit your changes: `git commit -m "feat: describe your changes"`
6. Push the branch: `git push origin feature/your-feature`
7. Create a Pull Request

#### 📝 Commit Convention

Follow the Angular commit convention:

| Type | Description |
|------|-------------|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `docs:` | Documentation update |
| `refactor:` | Code refactoring |
| `test:` | Test-related |
| `chore:` | Build/tooling related |

#### 🐛 Reporting Issues

Please submit bugs or feature requests via [GitHub Issues](https://github.com/gitstq/DataDiffForge/issues). Include:

- Problem description
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment info (Python version, OS)

---

### 📄 License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

```
MIT License

Copyright (c) 2026 gitstq

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/gitstq">gitstq</a>
</p>
