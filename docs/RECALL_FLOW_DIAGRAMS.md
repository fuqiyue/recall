# Recall 可视化流程图

本文档包含 Recall 系统的所有核心流程图，使用 Mermaid 格式便于在 GitHub 和支持 Mermaid 的编辑器中直接渲染。

---

## 1. 文档结构总览

```mermaid
flowchart TB
    subgraph 发布版本（唯一）
        A[logic_readme.md<br/>当前生效规则<br/>最新版本]
        B[logic_change.md<br/>活跃修改记录<br/>未生效]
    end
    
    subgraph 代码库
        E[实际代码]
        F[测试代码]
    end
    
    subgraph 历史归档（多个版本）
        C[logic_version/records/<br/>已完成的决策记录]
        D[logic_version/index.md<br/>历史索引]
    end
    
    A -->|修改完成后更新| A
    B -->|完成后归档| C
    C -->|索引| D
    A -.->|指导| E
    E -.->|验证| F
    
    style A fill:#90EE90
    style B fill:#FFD700
    style C fill:#87CEEB
```

**核心原则**：
- `logic_readme.md` = 当前唯一真相
- `logic_change.md` = 正在进行的修改（临时）
- `logic_version/` = 历史记录（只读，用于回忆）

---

## 2. 三条修改通道

```mermaid
flowchart TD
    Start[收到修改需求] --> Judge{判断复杂度}
    
    Judge -->|简单Bug| Simple[简单修复通道]
    Judge -->|中等变更| Medium[中等变更通道]
    Judge -->|高风险| High[高风险通道]
    
    Simple --> S1[读取相关规则<br>logic_readme.md]
    S1 --> S2[查看目标代码<br>和直接调用方]
    S2 --> S3[检查直接测试]
    S3 --> S4[快速修复]
    S4 --> S5{是否改变<br>现有规则?}
    S5 -->|是| S6[更新 logic_readme.md]
    S5 -->|否| End[完成]
    S6 --> End
    
    Medium --> M1[读取 logic_readme.md<br>和 logic_change.md]
    M1 --> M2[给出修改计划<br>和影响范围]
    M2 --> M3{用户确认?}
    M3 -->|否| M2
    M3 -->|是| M4[实施修改]
    M4 --> M5[更新 logic_readme.md<br>可选记录到 logic_change.md]
    M5 --> End
    
    High --> H1[Recall：读取历史决策<br>logic_version/]
    H1 --> H2[查找消费者<br>和依赖关系]
    H2 --> H3[分析替代方案<br>A/B/C]
    H3 --> H4[评估迁移和回滚]
    H4 --> H5{决策检查点:<br>用户确认方案?}
    H5 -->|否| H3
    H5 -->|是| H6[创建 logic_change.md 记录]
    H6 --> H7[实施修改]
    H7 --> H8[代码语义审查]
    H8 --> H9[更新 logic_readme.md]
    H9 --> H10[归档到 logic_version/]
    H10 --> H11[关闭 logic_change.md 记录]
    H11 --> End
    
    style Simple fill:#90EE90
    style Medium fill:#FFD700
    style High fill:#FF6B6B
    style End fill:#87CEEB
```

**举例说明**：
- **简单Bug**：UI 显示错误、简单的逻辑修正
- **中等变更**：添加新功能、修改多个文件
- **高风险**：API 修改、数据库迁移、架构重构、V1/V2 兼容问题

---

## 3. 高风险通道 Recall 机制详解

```mermaid
sequenceDiagram
    participant User as 用户
    participant AI as AI助手
    participant LR as logic_readme.md
    participant LC as logic_change.md
    participant LV as logic_version/
    participant Code as 代码库

    User->>AI: 需要修改某个功能
    AI->>LR: 1. 读取当前规则
    AI->>LC: 2. 检查是否有活跃修改
    AI->>LV: 3. Recall：为什么这么设计？
    LV-->>AI: 返回历史决策记录
    AI->>Code: 4. 查找消费者和依赖
    Code-->>AI: 返回影响范围
    
    Note over AI: 5. 分析三种方案<br>A: 最小修改<br>B: 结构调整<br>C: 保持现状
    AI->>AI: 
    
    AI->>User: 6. 决策检查点：<br>• 历史原因<br>• 影响范围<br>• 三种方案对比<br>• 迁移/回滚计划
    User->>AI: 7. 选择方案B
    
    AI->>LC: 8. 创建 CHG 记录
    AI->>Code: 9. 实施修改
    AI->>AI: 10. 代码语义审查
    AI->>LR: 11. 更新当前规则
    AI->>LV: 12. 归档决策记录
    AI->>LC: 13. 关闭 CHG 记录
    AI->>User: 14. 完成！
```

---

## 4. 避免 V1/V2 过度兼容

```mermaid
flowchart TD
    Start[需要迭代功能] --> Check{项目是否<br>已上线?}
    
    Check -->|未上线| Strategy1[策略1：直接重构<br>不需要兼容V1]
    Check -->|已上线| Strategy2[策略2：需要兼容]
    
    Strategy1 --> Record1[在 logic_change.md 记录:<br>• 项目未上线<br>• 直接重构V1代码<br>• 无需迁移逻辑]
    
    Strategy2 --> Analyze[分析真实消费者]
    Analyze --> Decision{是否有<br>真实V1用户?}
    
    Decision -->|有| Compat[设计兼容方案<br>记录迁移计划]
    Decision -->|无| Strategy1
    
    Record1 --> Update[更新 logic_readme.md]
    Compat --> Update
    
    Update -->|是| UpdateDoc[更新 logic_readme.md]
    Update -->|否| Done[避免冗余代码]
    
    UpdateDoc --> Archive{高风险?}
    Archive -->|是| Save[归档到 logic_version/]
    Archive -->|否| Done
    
    Save --> Close[关闭 logic_change.md 记录]
    Close --> Done
    
    style Strategy1 fill:#90EE90
    style Strategy2 fill:#FFD700
    style Done fill:#87CEEB
```

**关键点**：AI 不会自动知道项目是否上线，需要在 `logic_readme.md` 中明确记录当前状态和真实消费者。

---

## 5. 与其他工具的兼容性

```mermaid
flowchart LR
    subgraph 外部来源
        Plan[Codex Plan]
        Spec[Spec Kit/Kiro Specs]
        Steering[Kiro Steering<br>product.md<br>tech.md<br>structure.md]
    end
    
    subgraph Recall 体系
        LR[logic_readme.md<br>当前规则]
        LC[logic_change.md<br>活跃修改]
        LV[logic_version/<br>历史决策]
    end
    
    Plan -.->|提供需求来源| LC
    Spec -.->|提供规格| LC
    Steering -.->|提供背景| LR
    
    LC -->|完成后| LR
    LR -->|归档| LV
    
    style LR fill:#90EE90
    style LC fill:#FFD700
    style LV fill:#87CEEB
```

**组合使用示例**：
1. **Kiro Steering** 提供长期背景（product.md / tech.md / structure.md）
2. **Spec Kit** 提供具体规格和需求
3. **Recall** 记录"为什么这么实现"的决策逻辑
4. **Codex Plan** 提供一次性实施计划

---

## 6. 日常工作流程

```mermaid
flowchart TD
    Daily[日常开发] --> Task{收到任务}
    
    Task --> Read1[1. 先读 logic_readme.md<br>了解当前规则]
    Read1 --> Read2[2. 检查 logic_change.md<br>是否有并行修改]
    Read2 --> Read3[3. 查看相关代码]
    Read3 --> Judge{判断通道}
    
    Judge -->|简单| Quick[快速修复<br>不创建记录]
    Judge -->|中等| Plan[先给计划<br>可选创建CHG]
    Judge -->|高风险| Recall[完整Recall<br>必须创建CHG]
    
    Quick --> Code1[修改代码]
    Plan --> Code1
    Recall --> Code1
    
    Code1 --> Test[测试]
    Test --> Pass{通过?}
    Pass -->|否| Code1
    Pass -->|是| Update{规则变化?}
    
    Update -->|是| UpdateDoc[更新 logic_readme.md]
    Update -->|否| Done[完成]
    
    UpdateDoc --> Archive{高风险?}
    Archive -->|是| Save[归档到 logic_version/]
    Archive -->|否| Done
    
    Save --> Close[关闭 logic_change.md 记录]
    Close --> Done
    
    style Read1 fill:#E3F2FD
    style Quick fill:#90EE90
    style Plan fill:#FFD700
    style Recall fill:#FF6B6B
    style Done fill:#87CEEB
```

---

## 7. 核心设计原则

```mermaid
mindmap
  root((Recall<br>核心原则))
    单一真相源
      logic_readme.md 唯一
      logic_change.md 唯一
      避免多份修改意见
    分层管理
      当前：logic_readme.md
      进行中：logic_change.md
      历史：logic_version/
    三条通道
      简单：快速修复
      中等：计划优先
      高风险：完整分析
    避免过度设计
      检查是否上线
      分析真实消费者
      避免V1/V2冗余
    可审计性
      记录决策原因
      保存关键取舍
      可追溯历史
    模块化兼容
      可接入 Spec Kit
      可接入 Kiro Steering
      可接入 Codex Plan
```

**与访问精神的契合度**：
- ✅ 记录"为什么这么设计"
- ✅ 避免"按下这头翘起那头"
- ✅ 防止 V1/V2 过度兼容
- ✅ 三条通道避免过度流程化
- ✅ 单一真相源（logic_readme.md）
- ✅ 可与其他工具组合使用

---

## 8. 正确方式 vs 错误方式

```mermaid
flowchart LR
    subgraph ❌ 错误方式
        Bad1[收到Bug] --> Bad2[直接让AI修复]
        Bad2 --> Bad3[AI只看当前代码]
        Bad3 --> Bad4[实施修改]
        Bad4 --> Bad5[Bug修复了<br>但破坏了其他功能]
        style Bad5 fill:#FF6B6B
    end
    
    subgraph ✅ 正确方式（Recall）
        Good1[收到Bug] --> Good2[读取 logic_readme.md]
        Good2 --> Good3{高风险?}
        Good3 -->|是| Good4[Recall 历史决策]
        Good4 --> Good5[为什么这么设计?]
        Good5 --> Good6[分析影响范围]
        Good6 --> Good7[提供方案对比]
        Good7 --> Good8[用户决策]
        Good8 --> Good9[实施修改]
        Good9 --> Good10[更新文档]
        Good10 --> Good11[Bug修复<br>且不破坏设计]
        style Good11 fill:#90EE90
    end
```

---

## 如何在项目中使用这些流程图

1. **在 Markdown 文件中引用**：
   ```markdown
   详见流程图：[Recall 流程图](docs/RECALL_FLOW_DIAGRAMS.md#1-文档结构总览)
   ```

2. **在 GitHub 中自动渲染**：
   - GitHub 原生支持 Mermaid 语法
   - 直接查看本文件即可看到渲染效果

3. **在编辑器中预览**：
   - VS Code：安装 "Markdown Preview Mermaid Support" 插件
   - Typora：内置支持
   - Obsidian：内置支持

4. **导出为图片**：
   - 使用 Mermaid Live Editor：https://mermaid.live/
   - 复制代码 → 导出为 PNG/SVG

---

## 许可

本文档遵循项目的 MIT 许可证。
