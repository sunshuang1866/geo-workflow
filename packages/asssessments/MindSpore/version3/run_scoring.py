import json, datetime
from collections import Counter

BASE = "/root/workspace/GEO-Search-Assessment/MindSpore/version3"

with open(f"{BASE}/responses.json") as f:
    data = json.load(f)
responses_list = data.get("responses", [])
responses = {r["question_id"]: r for r in responses_list}

with open(f"{BASE}/content-labels.json") as f:
    labels_data = json.load(f)
labels = {l["question_id"]: l for l in labels_data["labels"]}

official_domains = ["mindspore.cn", "gitcode.com/mindspore", "github.com/mindspore-ai", "gitee.com/mindspore"]

# LLM scoring results (evaluated by Claude inline)
LLM_SCORES = {
  "q_001": {"citation_type":"D","official_source_ratio":0.71,"accuracy_score":8,"issues_found":["missing_edge_cases"],"details":"覆盖ARM安装与opp_kernel错误排查，5/7引用为官方源，CANN文档引用合理，内容准确"},
  "q_002": {"citation_type":"E","official_source_ratio":0.33,"accuracy_score":6,"issues_found":["missing_scope","no_query_variants"],"details":"大量依赖mindnlp.readthedocs.io（第三方），仅gitee README为官方源，内容基本正确但官方引用比例低"},
  "q_003": {"citation_type":"E","official_source_ratio":0.43,"accuracy_score":7,"issues_found":["missing_scope","outdated_info"],"details":"r2.6 GPU安装文档正确引用，但NVIDIA/华为云博客占多数；版本特定内容准确"},
  "q_004": {"citation_type":"D","official_source_ratio":1.00,"accuracy_score":9,"issues_found":[],"details":"7/7全部引用官方源，infer_faq/load_checkpoint/operator_comparison均为准确官方页面，内容质量高"},
  "q_006": {"citation_type":"E","official_source_ratio":0.43,"accuracy_score":7,"issues_found":["missing_scope","outdated_info"],"details":"r1.11 Docker文档引用正确，但大量依赖昇腾/华为云文档（第三方）；内容对旧版本问题有针对性"},
  "q_007": {"citation_type":"C","official_source_ratio":0.50,"accuracy_score":3,"issues_found":["fabricated_claims","negation_missed","version_confusion"],"details":"声称vLLM有mindspore后端支持（vLLM官方未提供MindSpore后端），github.com/vllm-project/vllm/issues/mindspore为虚构路径，核心技术信息不实"},
  "q_008": {"citation_type":"E","official_source_ratio":0.50,"accuracy_score":7,"issues_found":["missing_scope"],"details":"Docker安装文档正确引用，内容准确；官方/第三方源1:1，整体可用"},
  "q_009": {"citation_type":"D","official_source_ratio":0.83,"accuracy_score":9,"issues_found":[],"details":"5/6引用官方Lite文档，install_windows/quick_start/api_python页面均真实存在，内容完整准确"},
  "q_010": {"citation_type":"D","official_source_ratio":0.80,"accuracy_score":9,"issues_found":[],"details":"4/5引用官方源，安装方式（pip/conda/Docker/源码）覆盖完整，内容准确"},
  "q_011": {"citation_type":"D","official_source_ratio":0.67,"accuracy_score":8,"issues_found":[],"details":"DistributedSampler/MindDataset API引用准确，分布式数据分片内容正确"},
  "q_012": {"citation_type":"D","official_source_ratio":0.60,"accuracy_score":8,"issues_found":["missing_scope"],"details":"官方models仓库和YOLOv5教程引用正确，内容准确；未说明适用版本"},
  "q_013": {"citation_type":"D","official_source_ratio":0.67,"accuracy_score":7,"issues_found":["fabricated_claims","missing_edge_cases"],"details":"operator_comparison/Conv2d API引用准确，但community/issues/precision为非标准URL格式（疑为虚构路径）"},
  "q_014": {"citation_type":"C","official_source_ratio":0.50,"accuracy_score":3,"issues_found":["fabricated_claims","negation_missed","version_confusion"],"details":"使用export_from_onnx() API（MindSpore公开API中不存在），ONNX转MindIR应通过converter_lite工具，核心转换方式错误"},
  "q_015": {"citation_type":"C","official_source_ratio":0.40,"accuracy_score":3,"issues_found":["fabricated_claims","negation_missed","no_process_doc"],"details":"使用export_from_torch()函数（MindSpore公开API中不存在），PyTorch模型转换需通过mindconverter或手动重写，提供了虚构API调用"},
  "q_016": {"citation_type":"E","official_source_ratio":0.50,"accuracy_score":6,"issues_found":["missing_scope","negation_missed"],"details":"data sink模式动态切换数据集存在限制，回答暗示支持但未明确说明官方限制；引用正确但覆盖不完整"},
  "q_017": {"citation_type":"D","official_source_ratio":0.57,"accuracy_score":6,"issues_found":["vague_numbers","fabricated_claims"],"details":"version.html/CHANGELOG正确引用，但'PyNative性能提升约40%'等具体数字未在引用源中得到验证，blog URL可能不存在"},
  "q_018": {"citation_type":"D","official_source_ratio":0.60,"accuracy_score":8,"issues_found":["missing_use_cases"],"details":"PyNative/Graph模式对比表准确，context.html引用正确，缺少具体场景决策框架"},
  "q_019": {"citation_type":"C","official_source_ratio":0.50,"accuracy_score":3,"issues_found":["fabricated_claims","negation_missed"],"details":"表格中export_from_torch为虚构API，MindSpore不直接支持读取PyTorch/TF/Caffe模型（需模型转换工具），提供了误导性的支持矩阵"},
  "q_020": {"citation_type":"E","official_source_ratio":0.40,"accuracy_score":7,"issues_found":["shallow_content","missing_use_cases"],"details":"TransData API文档引用正确，算子功能描述准确，但性能优化建议较浅显，缺少具体使用场景示例"},
  "q_021": {"citation_type":"D","official_source_ratio":0.60,"accuracy_score":8,"issues_found":["missing_edge_cases"],"details":"tensor_dtype_promotion文档引用正确，类型提升规则对比准确，未涵盖全部边界条件"},
  "q_025": {"citation_type":"E","official_source_ratio":0.29,"accuracy_score":7,"issues_found":["missing_scope","shallow_content"],"details":"大量引用hiascend.com和华为开发者联盟，官方MindSpore定位说明仅引用首页；内容基本正确但官方引用不足"},
  "q_027": {"citation_type":"D","official_source_ratio":0.80,"accuracy_score":7,"issues_found":["vague_numbers","outdated_info"],"details":"releases/version.html引用正确，但版本历史表中具体发布日期（如2.0-2022-03）无直接来源支持"},
  "q_029": {"citation_type":"E","official_source_ratio":0.29,"accuracy_score":6,"issues_found":["missing_scope","shallow_content","no_reasoning"],"details":"英文回答，引用huggingface.co暗示MindSpore与HuggingFace深度集成（实际支持有限），官方引用比例低（2/7）"},
  "q_032": {"citation_type":"C","official_source_ratio":0.67,"accuracy_score":2,"issues_found":["fabricated_claims","no_evidence","vague_numbers"],"details":"包含虚构的2026年活动安排（MindSpore Summit 2026具体日期、HDC 2026），'5000+开发者'等数据无来源，属于内容捏造"},
  "q_034": {"citation_type":"C","official_source_ratio":0.17,"accuracy_score":3,"issues_found":["fabricated_claims","vague_numbers","no_evidence","missing_scope"],"details":"提供具体性能数据（ResNet50约2ms、YOLOv5s约15ms）但无官方基准测试引用，与TFLite/NCNN对比数据属于虚构基准"},
  "q_035": {"citation_type":"C","official_source_ratio":0.71,"accuracy_score":5,"issues_found":["entity_confusion","ambiguous_terminology"],"details":"声称MindSpore遵循'OpenI开源基金会治理模式'——OpenI是AI开发平台而非管理MindSpore的基金会，属于实体混淆错误"},
  "q_036": {"citation_type":"C","official_source_ratio":1.00,"accuracy_score":3,"issues_found":["fabricated_claims","no_evidence"],"details":"community/issues/6789用作SIG例会安排来源，具体会议时间（周四19:00-20:00）无法从该来源核实，系虚构内容"},
  "q_038": {"citation_type":"C","official_source_ratio":0.83,"accuracy_score":3,"issues_found":["fabricated_claims","no_evidence"],"details":"LLM Inference Serving SIG例会频率和工作重点引用community/issues/6789，具体会议安排无法核实"},
  "q_040": {"citation_type":"C","official_source_ratio":0.83,"accuracy_score":3,"issues_found":["fabricated_claims","no_evidence"],"details":"Parallel Training SIG工作范围和例会安排同样依赖issues/6789这一可疑来源"},
  "q_041": {"citation_type":"C","official_source_ratio":0.83,"accuracy_score":5,"issues_found":["fabricated_claims","no_evidence"],"details":"MindQuantum作为真实产品存在，文档URL有效，但SIG例会安排同样依赖issues/6789"},
  "q_043": {"citation_type":"D","official_source_ratio":0.86,"accuracy_score":8,"issues_found":[],"details":"governance.md/sig-charter.md为真实官方治理文档，申请成立SIG流程描述基于真实文档"},
  "q_045": {"citation_type":"D","official_source_ratio":1.00,"accuracy_score":9,"issues_found":[],"details":"全部引用tsc-charter.md/governance.md等真实官方文档，TSC职责描述准确"},
  "q_047": {"citation_type":"C","official_source_ratio":0.88,"accuracy_score":3,"issues_found":["fabricated_claims","no_evidence"],"details":"SIG列表及例会频率以issues/6789为主要来源，该issue不太可能是官方SIG注册表，具体信息无法核实"},
  "q_048": {"citation_type":"C","official_source_ratio":0.67,"accuracy_score":3,"issues_found":["fabricated_claims","no_evidence","vague_numbers"],"details":"声称MindSpore在KubeCon EU 2022发表了具体主题演讲，引用gitee社区为来源无法核实，疑似捏造会议信息"},
  "q_052": {"citation_type":"C","official_source_ratio":0.83,"accuracy_score":5,"issues_found":["entity_confusion","ambiguous_terminology"],"details":"将MindSpore邮件列表归属于OpenI平台，但MindSpore邮件服务实际托管于mailweb.mindspore.cn，属于平台归属错误"},
  "q_054": {"citation_type":"C","official_source_ratio":0.50,"accuracy_score":3,"issues_found":["entity_confusion","fabricated_claims","ambiguous_terminology"],"details":"将'开放原子开源基金会'与'OpenI'混用（两者是不同组织），邮件系统来源描述存在严重实体混淆"},
  "q_055": {"citation_type":"C","official_source_ratio":0.80,"accuracy_score":5,"issues_found":["entity_confusion","ambiguous_terminology"],"details":"邮件列表以OpenI为主要平台来源，但mindspore.cn邮件服务实际基础设施归属存在混淆"},
  "q_059": {"citation_type":"C","official_source_ratio":0.83,"accuracy_score":4,"issues_found":["fabricated_claims","no_evidence"],"details":"声称MeetingBot已于'2024年中下线'并给出具体下线原因，该信息无官方来源支持，属于捏造历史事件"},
  "q_063": {"citation_type":"D","official_source_ratio":0.86,"accuracy_score":8,"issues_found":[],"details":"security/security/report/security-policy.md均为真实官方安全文档，漏洞处理流程描述准确"},
  "q_064": {"citation_type":"D","official_source_ratio":0.83,"accuracy_score":8,"issues_found":[],"details":"tsc-charter.md/governance.md引用正确，TSC会议公开性和治理参与描述基于真实章程文档"},
}

# ─── Build result objects ──────────────────────────────────────────────────
def assign_severity(citation_type, ratio, score, content_coverage):
    if citation_type == "C":
        return "P0"
    if citation_type == "B":
        return "P1"  # will elevate if full coverage
    if citation_type == "E":
        return "P1"
    if citation_type == "D":
        return "no_action" if score >= 8 else "P2"
    return "P2"

results = []

# Phenomenon A first
for qid, label in labels.items():
    if not label["content_exists"]:
        r = responses.get(qid, {})
        results.append({
            "question_id": qid,
            "question": label["question"],
            "platform": "qwen",
            "content_exists": False,
            "citation_type": "A",
            "official_source_ratio": 0.0,
            "accuracy_score": None,
            "severity": "P0",
            "details": "官方站点无针对此问题的专项内容（人工标注）",
            "issues_found": ["no_content"],
            "sources_identified": []
        })

# Layer 2 results
for qid, score_data in LLM_SCORES.items():
    label = labels[qid]
    r = responses[qid]
    citations = r.get("citations", [])
    sources = [{"url_or_name": u, "type": "official" if any(d in u for d in official_domains) else "third-party"} for u in citations]
    severity = assign_severity(score_data["citation_type"], score_data["official_source_ratio"], score_data["accuracy_score"], label["content_coverage"])
    results.append({
        "question_id": qid,
        "question": label["question"],
        "platform": "qwen",
        "content_exists": True,
        "content_coverage": label["content_coverage"],
        "citation_type": score_data["citation_type"],
        "official_source_ratio": score_data["official_source_ratio"],
        "accuracy_score": score_data["accuracy_score"],
        "severity": severity,
        "details": score_data["details"],
        "issues_found": score_data["issues_found"],
        "sources_identified": sources
    })

results.sort(key=lambda x: ({"P0":0,"P1":1,"P2":2,"no_action":3}.get(x["severity"],4), x["question_id"]))

# ─── Cross-platform patterns (single platform) ────────────────────────────
patterns = {
    "hallucination_patterns": [
        {"trigger": "模型转换API（export_from_torch/export_from_onnx）", "platforms": ["qwen"], "example": "q_014/q_015/q_019: 虚构API函数名，MindSpore实际使用converter_lite工具", "question_ids": ["q_014","q_015","q_019"]},
        {"trigger": "SIG例会安排（issues/6789）", "platforms": ["qwen"], "example": "q_036/q_038/q_040/q_047: 用单一issue号捏造多个SIG的具体例会时间", "question_ids": ["q_036","q_038","q_040","q_041","q_047"]},
        {"trigger": "未来活动规划（2026年）", "platforms": ["qwen"], "example": "q_032: 虚构MindSpore Summit 2026具体日期和参与人数", "question_ids": ["q_032"]},
        {"trigger": "会议/活动历史（KubeCon等）", "platforms": ["qwen"], "example": "q_048: 虚构KubeCon EU 2022具体演讲主题", "question_ids": ["q_048"]},
        {"trigger": "vLLM + MindSpore集成", "platforms": ["qwen"], "example": "q_007: 虚构vLLM MindSpore后端支持", "question_ids": ["q_007"]},
    ],
    "disambiguation_patterns": [
        {"term": "OpenI vs 开放原子开源基金会", "confused_with": "OpenI（openi.org.cn）被误作开放原子基金会或MindSpore治理基金会", "platforms": ["qwen"], "question_ids": ["q_035","q_052","q_054","q_055"]},
        {"term": "MindSpore邮件列表平台", "confused_with": "归属于openi.org.cn而非mailweb.mindspore.cn", "platforms": ["qwen"], "question_ids": ["q_052","q_054","q_055"]},
        {"term": "MindMeetingBot自动化工具", "confused_with": "虚构的服务下线历史和原因", "platforms": ["qwen"], "question_ids": ["q_059"]},
    ],
    "negation_failures": [
        {"fact": "MindSpore不直接支持读取PyTorch/TF模型（需转换工具）", "platforms_missed": ["qwen"], "question_ids": ["q_019"]},
        {"fact": "MindSpore没有export_from_torch/export_from_onnx公开API", "platforms_missed": ["qwen"], "question_ids": ["q_014","q_015"]},
        {"fact": "vLLM官方不提供MindSpore后端", "platforms_missed": ["qwen"], "question_ids": ["q_007"]},
    ],
    "citation_gaps": [
        {"topic": "SIG注册表和例会安排", "suggested_page": "gitee.com/mindspore/community 缺少结构化SIG注册表页面"},
        {"topic": "MindSpore邮件列表订阅地址", "suggested_page": "mailweb.mindspore.cn 缺少官方文档说明"},
        {"topic": "模型转换工具（converter_lite/mindconverter）", "suggested_page": "mindspore.cn/lite/docs 转换工具独立文档"},
        {"topic": "端侧框架性能基准测试", "suggested_page": "mindspore.cn/lite 缺少与TFLite/NCNN的官方对比基准"},
        {"topic": "华为AI生态中MindSpore定位说明", "suggested_page": "mindspore.cn 缺少与昇腾/CANN关系的定位页面"},
    ],
    "content_origin_issues": [
        {"issue": "SIG例会信息无结构化官方来源", "affected_platforms": ["qwen"], "question_ids": ["q_036","q_038","q_040","q_041","q_047"], "note": "单平台，但问题属于内容缺口"},
        {"issue": "模型转换API文档不明确导致幻觉", "affected_platforms": ["qwen"], "question_ids": ["q_014","q_015","q_019"], "note": "官方文档缺少明确的API vs工具边界说明"},
        {"issue": "邮件列表平台说明缺失", "affected_platforms": ["qwen"], "question_ids": ["q_052","q_054","q_055"], "note": "mailweb.mindspore.cn缺少官方文档入口"},
    ]
}

# ─── Generate suggestions ─────────────────────────────────────────────────
# Phenomenon→catalog mapping (abbreviated for key items)
CATALOG_HINTS = {
    "A": ["CTX-01","CTX-02","CTX-03","ORG-01","ORG-02","REF-01"],
    "B": ["CTX-02","CTX-03","ORG-04","DIS-01","KWD-01","SITE-01"],
    "C": ["CTX-04","REF-04","REF-07","DIS-01","DIS-03","NEG-01","NEG-02","VER-01"],
    "D": ["REF-06","EXC-01","EXC-08","SITE-05"],
    "E": ["CTX-02","CTX-03","CTX-08","REF-02","REF-03","EXC-06","EXC-08"],
}
ISSUE_CATALOG = {
    "fabricated_claims": ["REF-04","REF-10","NEG-03","DIS-03"],
    "negation_missed": ["NEG-01","NEG-02","NEG-04"],
    "entity_confusion": ["REF-07","DIS-01","DIS-02"],
    "ambiguous_terminology": ["DIS-01","DIS-02","DIS-03","CTX-04"],
    "missing_scope": ["CTX-05","EXP-10"],
    "outdated_info": ["REF-06","VER-01","VER-02"],
    "version_confusion": ["VER-01","VER-02","CTX-05"],
    "vague_numbers": ["REF-01","EXP-08"],
    "shallow_content": ["EXC-08","EXC-06","REF-02"],
    "no_evidence": ["REF-04","REF-05","EXC-01"],
    "no_process_doc": ["EXP-03","REF-05"],
    "missing_use_cases": ["CTX-08","EXC-07"],
    "missing_edge_cases": ["EPT-06","CTX-05"],
    "no_query_variants": ["CTX-03","KWD-01"],
    "no_reasoning": ["EPT-08","REF-04"],
}

suggestions = []
sid = 1

# Group C results by issue pattern for consolidation
phenomenon_a_qids = [l["question_id"] for l in labels_data["labels"] if not l["content_exists"]]

# Consolidated suggestion for Phenomenon A
if phenomenon_a_qids:
    suggestions.append({
        "suggestion_id": f"s_{sid:03d}", "sid": sid,
        "question_ids": phenomenon_a_qids,
        "question": "（多问题）行业对比/选型/专项故障类问题无官方内容",
        "platform": "qwen",
        "citation_type": "A",
        "official_source_ratio": 0.0,
        "accuracy_score": None,
        "severity": "P0",
        "category": "content",
        "catalog_refs": ["CTX-01","CTX-02","CTX-03","CTX-06","CTX-08"],
        "suggestion_text": "针对7个无官方内容问题，按类型分批创建专项文档：(1) 竞品对比页面（MindSpore vs PyTorch/PaddlePaddle/TensorFlow）：在官网创建选型指南，以客观对比表呈现，重点突出昇腾NPU适配优势；(2) 行业定位页面：明确MindSpore在华为AI全栈中的角色；(3) MindNLP昇腾设备故障排查页面：补充官方文档",
        "is_content_origin": True,
        "affected_count": len(phenomenon_a_qids)
    })
    sid += 1

# Model conversion fabrication (q_014, q_015, q_019)
suggestions.append({
    "suggestion_id": f"s_{sid:03d}", "sid": sid,
    "question_ids": ["q_014","q_015","q_019"],
    "question": "模型转换API幻觉（export_from_torch/export_from_onnx）",
    "platform": "qwen",
    "citation_type": "C",
    "official_source_ratio": 0.47,
    "accuracy_score": 3,
    "severity": "P0",
    "category": "correction",
    "catalog_refs": ["REF-04","NEG-03","DIS-03","CTX-04","NEG-01"],
    "suggestion_text": "在官方模型转换文档中明确声明：MindSpore不提供export_from_torch()或export_from_onnx()公开API。创建专项的'模型迁移指南'页面，清晰区分：(1) 使用converter_lite工具转换ONNX→MindIR；(2) 使用MindConverter工具从PyTorch迁移；(3) 添加显著的否定声明框：'MindSpore暂不支持直接加载PyTorch/TensorFlow原生格式'，防止AI平台误解",
    "is_content_origin": True,
    "affected_count": 3
})
sid += 1

# SIG meeting schedule fabrication (q_036, q_038, q_040, q_041, q_047)
suggestions.append({
    "suggestion_id": f"s_{sid:03d}", "sid": sid,
    "question_ids": ["q_036","q_038","q_040","q_041","q_047"],
    "question": "SIG例会信息幻觉（issues/6789虚构来源）",
    "platform": "qwen",
    "citation_type": "C",
    "official_source_ratio": 0.87,
    "accuracy_score": 3,
    "severity": "P0",
    "category": "correction",
    "catalog_refs": ["REF-04","REF-05","ORG-05","CTX-01","EXP-03"],
    "suggestion_text": "在gitee.com/mindspore/community创建结构化SIG注册表页面（sig-list.md或专用目录），每个SIG包含：名称、负责人、例会频率、例会链接/入口、邮件列表。当前issues/6789被AI平台作为SIG信息来源，需将该信息从issue迁移至正式文档，并确保Google/Bing/百度可抓取",
    "is_content_origin": True,
    "affected_count": 5
})
sid += 1

# Mailing list entity confusion (q_052, q_054, q_055)
suggestions.append({
    "suggestion_id": f"s_{sid:03d}", "sid": sid,
    "question_ids": ["q_052","q_054","q_055"],
    "question": "邮件列表平台归属混淆（OpenI vs mailweb.mindspore.cn）",
    "platform": "qwen",
    "citation_type": "C",
    "official_source_ratio": 0.71,
    "accuracy_score": 4,
    "severity": "P0",
    "category": "correction",
    "catalog_refs": ["DIS-01","DIS-02","REF-07","CTX-04","DIS-03"],
    "suggestion_text": "在mindspore.cn/community下创建'邮件列表'专项说明页面，明确：(1) 邮件服务托管地址（mailweb.mindspore.cn）；(2) 与OpenI平台的关系（如有）；(3) 各邮件列表订阅入口和用途；(4) 在gitee.com/mindspore/community的README中添加邮件列表入口链接。消除AI平台对OpenI/OpenAtom/mindspore.cn之间关系的混淆",
    "is_content_origin": True,
    "affected_count": 3
})
sid += 1

# Fabricated future events (q_032)
suggestions.append({
    "suggestion_id": f"s_{sid:03d}", "sid": sid,
    "question_ids": ["q_032"],
    "question": "MindSpore 2026年活动规划（虚构事件）",
    "platform": "qwen",
    "citation_type": "C",
    "official_source_ratio": 0.67,
    "accuracy_score": 2,
    "severity": "P0",
    "category": "correction",
    "catalog_refs": ["REF-04","REF-05","CTX-01","ORG-01"],
    "suggestion_text": "在mindspore.cn/news或community/events创建官方活动日历页面，及时发布已确认的活动信息。对于尚未规划的未来活动，在官网添加明确说明：'年度活动计划将于Q1公布'，防止AI平台基于空缺内容生成虚假预测",
    "is_content_origin": False,
    "affected_count": 1
})
sid += 1

# vLLM fabrication (q_007)
suggestions.append({
    "suggestion_id": f"s_{sid:03d}", "sid": sid,
    "question_ids": ["q_007"],
    "question": "vLLM + MindSpore部署（虚构后端支持）",
    "platform": "qwen",
    "citation_type": "C",
    "official_source_ratio": 0.50,
    "accuracy_score": 3,
    "severity": "P0",
    "category": "correction",
    "catalog_refs": ["NEG-01","NEG-03","REF-04","CTX-05","DIS-03"],
    "suggestion_text": "在MindSpore Serving文档首页添加明确的集成状态说明：'MindSpore Serving是独立的推理服务框架，与vLLM不兼容（vLLM目前无MindSpore后端）'。如有集成规划，添加路线图说明。同时为LLM推理部署创建专项对比页面，说明MindSpore Serving vs vLLM的适用场景差异",
    "is_content_origin": False,
    "affected_count": 1
})
sid += 1

# Community contribution entity confusion (q_035)
suggestions.append({
    "suggestion_id": f"s_{sid:03d}", "sid": sid,
    "question_ids": ["q_035"],
    "question": "MindSpore社区贡献指南（OpenI治理模式混淆）",
    "platform": "qwen",
    "citation_type": "C",
    "official_source_ratio": 0.71,
    "accuracy_score": 5,
    "severity": "P0",
    "category": "correction",
    "catalog_refs": ["REF-07","DIS-01","CTX-04"],
    "suggestion_text": "在贡献指南和governance.md首段明确MindSpore的治理归属：'MindSpore社区遵循自有治理章程，由TSC负责技术决策。'消除与OpenI平台的混淆。在community首页添加'治理架构'简介卡片",
    "is_content_origin": False,
    "affected_count": 1
})
sid += 1

# Fabricated performance benchmarks (q_034)
suggestions.append({
    "suggestion_id": f"s_{sid:03d}", "sid": sid,
    "question_ids": ["q_034"],
    "question": "MindSpore Lite性能基准（虚构对比数据）",
    "platform": "qwen",
    "citation_type": "C",
    "official_source_ratio": 0.17,
    "accuracy_score": 3,
    "severity": "P0",
    "category": "correction",
    "catalog_refs": ["REF-04","REF-01","EXC-01","CTX-08","EXP-08"],
    "suggestion_text": "在mindspore.cn/lite发布官方基准测试报告，包含：测试硬件（Ascend 310/310P）、测试模型（ResNet50/YOLOv5等）、延迟/吞吐量数据、与TFLite/NCNN的对比（可选）。有了官方基准数据，AI平台将引用真实数据而非生成虚假数字",
    "is_content_origin": False,
    "affected_count": 1
})
sid += 1

# KubeCon fabrication (q_048)
suggestions.append({
    "suggestion_id": f"s_{sid:03d}", "sid": sid,
    "question_ids": ["q_048"],
    "question": "MindSpore国际峰会参与情况（虚构会议信息）",
    "platform": "qwen",
    "citation_type": "C",
    "official_source_ratio": 0.67,
    "accuracy_score": 3,
    "severity": "P0",
    "category": "correction",
    "catalog_refs": ["REF-05","REF-04","ORG-01"],
    "suggestion_text": "在mindspore.cn/community/events或news板块创建'国际交流'专项页面，列出MindSpore参与过的国际开源峰会（含演讲主题、链接）。若无此类活动，添加说明；若有，提供可引用的官方记录，防止AI平台凭空捏造参会历史",
    "is_content_origin": False,
    "affected_count": 1
})
sid += 1

# P1 suggestions - E phenomenon
suggestions.append({
    "suggestion_id": f"s_{sid:03d}", "sid": sid,
    "question_ids": ["q_002","q_003","q_006","q_008","q_016","q_020","q_025","q_029"],
    "question": "（多问题）官方引用比例不足（E类现象）",
    "platform": "qwen",
    "citation_type": "E",
    "official_source_ratio": 0.43,
    "accuracy_score": 6,
    "severity": "P1",
    "category": "optimization",
    "catalog_refs": ["CTX-02","CTX-03","EXC-06","EXC-08","REF-02","REF-03"],
    "suggestion_text": "8个E类问题共同特征：内容准确但官方文档深度不足，导致AI平台引用第三方博客补充。优化方向：(1) 为MindNLP/Docker/data sink等常见问题创建专项FAQ页面，以结论先行格式组织；(2) 提升文档的完整性（参数说明、版本适配表、常见错误代码），减少AI平台对华为云博客/知乎的依赖；(3) 为选型问题（q_025/q_029）创建官方定位说明，提供可引用的对比框架",
    "is_content_origin": True,
    "affected_count": 8
})
sid += 1

# P2 suggestions
suggestions.append({
    "suggestion_id": f"s_{sid:03d}", "sid": sid,
    "question_ids": ["q_013","q_017","q_027"],
    "question": "（多问题）D类轻微问题（可疑URL/未经验证数字）",
    "platform": "qwen",
    "citation_type": "D",
    "official_source_ratio": 0.68,
    "accuracy_score": 7,
    "severity": "P2",
    "category": "optimization",
    "catalog_refs": ["REF-06","VER-01","REF-01","EXC-08"],
    "suggestion_text": "3个P2问题：(1) q_013 Conv2d精度：community/issues/precision为非标准URL，建议在精度对比文档中添加官方issue入口链接；(2) q_017 v2.8.0特性：官网blog/mindspore-2-8-release若不存在，建议将发布说明整合到version.html，并避免未核实的性能百分比；(3) q_027版本节奏：建议在releases页面添加版本周期说明（如'约每半年发布一个主版本'），避免AI平台生成未经核实的历史日期",
    "is_content_origin": False,
    "affected_count": 3
})
sid += 1

# ─── Summary stats ────────────────────────────────────────────────────────
by_phenomenon = Counter()
by_severity = Counter()
for r in results:
    by_phenomenon[r["citation_type"]] += 1
    by_severity[r["severity"]] += 1

scored_pairs = len(LLM_SCORES)
total_pairs = len(labels)
avg_ratio = sum(v["official_source_ratio"] for v in LLM_SCORES.values()) / len(LLM_SCORES)

summary = {
    "by_phenomenon": dict(by_phenomenon),
    "by_severity": dict(by_severity),
    "by_platform": {
        "qwen": {
            "avg_score": round(sum(v["accuracy_score"] for v in LLM_SCORES.values()) / len(LLM_SCORES), 1),
            "avg_ratio": round(avg_ratio, 2)
        }
    }
}

# ─── Write scoring-results.json ───────────────────────────────────────────
output = {
    "metadata": {
        "scored_at": "2026-03-25T00:00:00Z",
        "total_questions": total_pairs,
        "total_platforms": 1,
        "platforms": ["qwen"],
        "total_pairs": total_pairs,
        "scored_pairs": scored_pairs,
        "skipped_pairs": 0,
        "has_standard_answers": False,
        "official_domains": ["mindspore.cn","gitcode.com/mindspore","github.com/mindspore-ai","gitee.com/mindspore"],
        "input_file": "MindSpore/version3/responses.json",
        "note": "Single-platform assessment (qwen only). Cross-platform comparison not available."
    },
    "results": results,
    "patterns": patterns,
    "summary": summary,
    "suggestions": suggestions
}

with open(f"{BASE}/scoring-results.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"scoring-results.json written")
print(f"  Total questions: {total_pairs}")
print(f"  Scored (Layer 2): {scored_pairs}")
print(f"  Phenomenon A: {by_phenomenon.get('A',0)}")
print(f"  Phenomenon C: {by_phenomenon.get('C',0)}")
print(f"  Phenomenon D: {by_phenomenon.get('D',0)}")
print(f"  Phenomenon E: {by_phenomenon.get('E',0)}")
print(f"  P0: {by_severity.get('P0',0)} | P1: {by_severity.get('P1',0)} | P2: {by_severity.get('P2',0)} | OK: {by_severity.get('no_action',0)}")
print(f"  Avg citation ratio (Layer 2): {avg_ratio:.1%}")
print(f"  Suggestions generated: {len(suggestions)}")
