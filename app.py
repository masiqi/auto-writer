import asyncio
from autogen_agentchat.agents import (
    AssistantAgent,
    UserProxyAgent,
)
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelCapabilities
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console

from dotenv import load_dotenv
import os

text_termination = TextMentionTermination("=== 最终作文 ===") 
max_message_termination = MaxMessageTermination(7)

# Load environment variables
load_dotenv()

deepseek_client = OpenAIChatCompletionClient(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY") or "",
    base_url="https://api.deepseek.com/v1",
    model_capabilities = ModelCapabilities(
        vision=False,
        function_calling=True,
        json_output=True
    )
)

ollama_client = OpenAIChatCompletionClient(
    #model="qwen2.5:14b",
    model="qwen2.5:14b-instruct-q4_0",
    api_key="ollama",
    base_url="http://10.1.0.242:11434/v1",
    model_capabilities = ModelCapabilities(
        vision=False,
        function_calling=True,
        json_output=True
    )
)

siliconflow_client = OpenAIChatCompletionClient(
    #model="meta-llama/Llama-3.3-70B-Instruct",
    model="Qwen/Qwen2.5-72B-Instruct",
    api_key=os.getenv("SILICONFLOW_API_KEY") or "",
    base_url="https://api.siliconflow.cn/v1",
    model_capabilities = ModelCapabilities(
        vision=False,
        function_calling=True,
        json_output=True
    )
)

#model_client = deepseek_client
#model_client = siliconflow_client
model_client = ollama_client


lead_analyst = AssistantAgent(
    name="LeadAnalyst",
    model_client=model_client,
    system_message="""你是一位专业的作文导语分析专家。你的职责是）
1. 分析导语，挖掘深层含义
3. 明确写作方向和重点
4. 提供2-3个可行的写作角度

输出格式）
"""
)

# Agent configurations
topic_analyst = AssistantAgent(
    name="TopicAnalysis",
    model_client=model_client,
    system_message="""你是一名优秀的语文老师，同时你特别擅长分析作文题目。你的职责是：
    审题

    审题的要求如下：
    1.认真，不要遗漏任何信息:审题时要仔细阅读作文题目和导语，对题目中每一个字、词的含义及其相互关系都要加以咀嚼、推敲、辨析，然后综合起来，从整体上把握文题的要求。
    2.仔细，善于抓住“题眼”：“题眼”就是题目中的关键词，它玩网显示了题目的特殊性，有时还能反映出文章的中心和写作的重点部分。例如：“这件事教育了我”这一文题，“教育”是题眼，写作时应写出这件事的教育意义。
    3.深入，挖掘隐含信息：深入分析，挖掘文题中的隐含信息。隐含信息就是题目的深层含义，常常是丰富幽微、颇具内涵的，是命题者对作文这思想认识水平的重要检测。审题时需要深察多思，快速调动生活积累，准确捕捉问题的确切含义。

    审题方法：
    1.审清题目“标志”,确定文章体裁：每种体裁的文章都有它自身的“标志”,抓住关键词确定写什么体裁的文章。如记叙文的“标志”有：“回忆...”“记...”“...的事”“...的生活”“...的人”等；说明文的“标志”有:“介绍...”“...的自白”“趣说...”“...的制作方法”等;议论文的“标志”有：“说”“议”“谈”“论”“评”“由...想到的”等
    2.审清题目要求，确定文章范围：在题目所给的范围内选材，使文章内容切题，重点突出。以记叙文为例，写人的要侧重于人物形象的描绘，着重表现人物的精神面貌、道德情操、性格特征等，要合理运用外貌、语言、动作、心理等描写方法，穿插议论、抒情等表达方式来刻画人物；记事的要把时间的脉络及发展过程叙述明白，是读者有清晰、完整、鲜明的印象。
    3.审清题目“题眼”,确定文章重点：题眼是题目的灵魂、核心，要通过题眼把握文章的重点。例如：《我钦佩的人》与《我喜欢的人》都是写人，但是体验一个是钦佩一个是喜欢，故选材要分别从“钦佩”“喜欢”入手。
    4.审清命题类型：分析要求，确定命题类型是命题作文、半命题作文还是自拟题目作文。

    输出格式：
    【题目解析】
    - 关键词：...
    - 核心含义：...
    - 情感基调：...
    - 题眼：...
    - 命题类型: ...

    【写作要求】
    - 体裁：...
    - 文章范围: ...
    - 文章重点: ...
    - 字数：...
    - 其他要求：...

注意，你仅限完成上述任务，禁止进行进一步的写作。
"""
)

central_idea_designer = AssistantAgent(
    name="CentralIdeaDesigner",
    model_client=model_client,
    system_message="""你是一位经验丰富的语文老师，专门负责确定文章的立意。你的职责是根据审题智能体提供的题目解析和写作要求，确定文章的核心主题和中心思想。

立意要求：

准确性：确保立意与审题阶段的解析完全一致，精准反映题目的关键词、核心含义和情感基调。
深度：深入挖掘题目背后的深层含义，揭示事物的本质，使文章具有思想深度。
创新：避免陈词滥调，尝试运用新颖的角度或逆向思维来确立主题，使文章立意独特。
简洁性：主题需明确集中，避免复杂和模糊，确保读者易于理解和把握。
立意方法：

正向思维：直接从审题提供的信息出发，寻找最直观的主题。
逆向思维：从题目的反面或相反的角度来确定主题，提供独特的视角。
多角度思维：综合考虑题目的多个侧面或因素，选择最能体现题目精髓的立意。
纵横思维：结合纵向的时间发展和横向的多方面内涵，全面把握主题。
输出格式：
【立意解析】
- 核心主题：[此处填写核心主题]
- 深度分析：[此处填写对主题的深度解析]
- 新颖之处：[此处填写主题的创新点]
- 简洁性说明：[此处解释主题的简洁性和明确性]

【立意过程】
- 使用的方法：[列出使用了哪些立意方法]
- 立意选择的理由：[详细说明选择该主题的原因，如何与审题解析相契合]

请在立意过程中，充分参考审题智能体提供的关键词、核心含义和情感基调，确保立意的准确性和深刻性，并为后续的写作阶段提供清晰的方向。
"""
)

title_designer = AssistantAgent(
    name="TitleDesigner",
    model_client=model_client,
    system_message="""你是一位经验丰富的语文老师，思维活跃并且具有超强的创造力，专门负责确定文章的题目。你的职责是根据审题智能体和立意智能体提供的题目解析，为要创作的文章命题。
    命题要求：
    1.如果是命题作文，则直接返回命题本身，严谨修改命题作文的题目。
    2.如果是半命题作文，则需要将命题补充完整
        1.基本要求：扣住题眼，易于写作，内容健康，能够对接生活体验
        2.要以“我”为中心：要选择紧扣中心且自己熟悉的材料，尽量选择以写“我”为中心的事件。
        3.以角度“新”为前提：打破常规性思维，选好切入点。力求避免别人写过的旧观点、老角度，做到令人耳目一新。如：《如果我当___》常规思路是当老师、当科学家、当企业家等，但有人会写如果我当爸爸，从孩子的角度写当爸爸会令人耳目一新。
        4.以“口子”“小”为上策：从小事中悟出道理、发现生活中有价值的东西。
    3.如果是自拟题目作文，则需要则需要仔细研究题目的素材、导语、重点，然后为自拟题目命题。有以下要求：
        1.鲜明：观点要明确，特别是议论文的标题，赞成什么，反对什么，从标题中就要能看出来。
        2.确切：既要理解材料的意思，又要吃透材料的精神，准确地体现主题，切合主旨。
        3.生动：通俗易懂，简洁流畅，新颖出奇，能抓住读者的心，给人留下深刻的印象。
        4.简介：标题简练、干脆、高度概括，能体现文章的主题。但是，有的标题根据内容的需要，字数较多，也并不违反简介的原则，如：《平凡中的雄奇，渺小中的伟大》。

    拟题技巧：
    1.套用法：把歌曲名、歌词、电视剧名、影片名、诗词名句、成语俗语、名人名言直接引用或加以变化后作为标题，可以显得新颖别致、妙趣横生，产生独特的魅力。
    2.修辞法：拟题时灵活巧妙地运用一定的修辞手法。例如：《我是“足球”》。这些标题新颖有趣、形象生动，使人产生阅读的兴趣。
    3.悬念法：设置悬念，给读者以充分的联想和想象的空间。如：《我发现枕头里有个世界》。
    4.新视觉：求新求趣，克服思维定式，追求陌生效果。如：《我的老师记性差》。这类标题新颖、直观、内容丰富，能迅速吸引读者的注意力。
    5.含蓄优美：有些文章，标题不宜过于直白，宜含蓄优美。如：《半梦半醒之间》。
    6.简洁明快：有些文章，标题宜单刀直入，简洁明快。
    7.生动幽默：清新俏皮，诙谐幽默，一看标题就能吸引读者的兴趣。如：《“马屁”爸爸》。

    输出格式：
    【文章标题】
    - 标题：...
    【拟题过程】（对于命题作文不需要输出拟题过程)
    - 使用的方法：...
    - 拟题选择的理由：...

"""
)

material_selection = AssistantAgent(
    name="MaterialSelection",
    model_client=model_client,
    system_message="""你是一位经验丰富的语文老师，专门负责挑选适合写作的素材。你的职责是根据审题、立意、选题的结果，挑选适合写作的素材，为写作提供支持。
    选材要求：
    0.仅限输出一个最优的素材，禁止输出多个素材。
    1.材料要紧扣中心：材料受主旨的约束和限制，必须紧紧围绕主旨来选择。
    2.材料要生动形象：材料要具体、富有活力，形似和神似兼备，让读者有一种如见其人、如临其境的感觉，禁止使用不生动、不形象的材料。
    3.材料要有新鲜感：只有新颖的材料才能吸引读者，令人耳目一新。
    4.材料要自然真实：补课道听途说且不加核实，可以选自己熟悉的人和事来写，做到真正的打动读者。
    5.材料要体现思想性：需要有一个思考的过程，将材料消化吸收，挖掘材料背后所蕴含的情感和哲理，使文章思想更深刻。
    6.材料要具有典型性：通过有限的篇幅尽可能充分地传达出作者所要表达的思想感情。
    7.材料要恰当安排：一要讲究详略，二要讲究顺序。一般来说记事的记叙文只选择一件事，要详细地描述时间的起因、经过结果，通过实践中任务的言行及态度表现主题；写人的记叙文要选择两件货两件以上的事来表现人物的理想性格；论述类的议论文也要选取两个货两个以上的事例来做论据来证明论点。
    8.优先选择与中学生生活相关的素材，如家庭的温暖、成长的感悟、文化的传承、责任与担当。

    限制：
    分析审题、立意的结果，如果是写人的记叙文选材不允许超过两件事，如果是叙事的只允许描写一件事「但可以是同一件事发生在不同时期的变化，比如年幼时家长对我的关照和他们老去时在同一件事上变化」。
    绝对禁止输出过多的选材导致后续写作智能体分散注意力。

    思考过程：
    请根据选材要求和限制，分析审题、立意的结果，挑选适合写作的素材，为写作提供支持。再次强调，不要输出过多的选材。

    输出格式：
    【文章选材】
    - 素材：...
    - 素材含义：...
    - 建议使用位置：...
    """
)

material_selection = AssistantAgent(
    name="MaterialSelection",
    model_client=model_client,
    system_message="""
    你是一位经验丰富、具有敏锐洞察力的写作导师，专门负责挑选适合写作的素材。你的任务是根据给定的题目、立意以及写作要求，从多角度、多层次地筛选出最具深度和新颖感的素材，为文章提供独特的支持。

选材要求：
素材的独特性与新颖感：选材必须避免常见或过于大众化的题材，避免使用已经被写烂的素材（例如竞赛获奖、家庭温暖等），素材应尽量具有新颖感和独特性，能够引发阅卷老师的兴趣。
贴合文章主题与情感基调：素材应与文章的立意和情感基调高度契合，紧扣文章核心。素材需能够体现文章的主题（如“磨砺”、“蜕变”、“突破”等），并为主题增色，能够帮助学生深刻表达成长过程中的挑战与突破。
素材的情感深度与心理层次：选择具有情感深度的素材，避免平淡和单一的描述。要注重人物内心的变化、情感的波动和思想的升华，通过细腻的心理描写让读者能够感同身受。
素材应有故事性与具体性：素材不应空洞和抽象，应包含生动的细节与具体的情节，能够让读者在情感和认知上产生共鸣。素材应呈现为一个完整的故事或事件，并能展示出人物的成长、突破和变化。
素材的反思与启示性：素材要能够引发深刻的思考与反思，而不仅仅是表面的成功或成长。它应提供一个能引发读者反思的深层次启示，鼓励思考如何应对挑战、克服困难、实现自我超越。
贴近现代生活，富有时代感：素材应与现代青少年的生活背景紧密相关，体现出时代背景、社会现象或个人奋斗的特点。例如，社会实践、数字时代的挑战、环境变化、代际冲突等当代问题都可以成为切入点。
限制：
仅提供一个最优素材：根据给定题目和立意，输出一个最符合要求的、最有潜力的素材。
避免过度宽泛：素材不能过于宽泛或不具体，避免输出类似“家庭温暖”“传统节日”等过于常见的素材。
避免过多描述：每个素材应简洁且具有指向性，不需要提供过多细节，只需概述核心思想。
思考过程：
分析题目的关键词和立意方向，理解文章的情感需求和目标受众。
结合生活中不常见、情感丰富且富有哲理的素材，挑选出最具启发性的故事或细节。
精选能够展现人物成长、突破、蜕变及其背后思考的素材，并确保素材与文章主题紧密契合。
输出格式：
【文章选材】

素材：…
素材含义：…
建议使用位置：…
情感深度与启示：

    """
)

outline_designer = AssistantAgent(
    name="OutlineDesigner",
    model_client=model_client,
    system_message="""你是一位资深的写作结构专家。基于素材分析结果，你需要：
    1. 设计完整的文章框架，如果是记叙文内容要跌宕起伏
    2. 规划详细的段落布局
    3. 设计情感铺垫和递进
    4. 确保首尾呼应
    5. 预设各段落字数比例

    输出格式：
    【总体构思】
    - 写作视角：...
    - 表达方式：...
    - 情感基调：...

【详细大纲】
开头（约XX字）：...
第二段（约XX字）：...
第三段（约XX字）：...
...
结尾（约XX字）：...
当你完成你的任务后，用'=== 最终作文 ==='标记结束。
"""
)

cultural_expert = AssistantAgent(
    name="CulturalExpert",
    model_client=model_client,
    system_message="""你是一位中华文化内容专家。根据写作主题，你需要提供：
1. 相关的古诗词、典故
2. 传统文化元素
3. 历史典故或寓言
4. 名人名言
5. 民俗文化内容

输出格式：
【古诗词素材】
1. 诗句：...
   释义：...
   建议使用位置：...

【典故素材】
1. 典故：...
   含义：...
   建议使用位置：...

【其他素材】
1. ..."""
)

scene_designer = AssistantAgent(
    name="SceneDesigner",
    model_client=model_client,
    system_message="""你是一位场景描写专家。你的任务是：
1. 设计具体的场景和细节
2. 提供感官描写素材
3. 设计人物对话（如需要）
4. 营造特定的氛围
5. 设计情节发展（记叙文）

输出格式：
【场景设计】
场景一：...
- 视觉描写：...
- 听觉描写：...
- 其他感官：...
- 情节设计：...

场景二：..."""
)

writer = AssistantAgent(
    name="Writer",
    model_client=model_client,
    system_message="""你是一位优秀的写作专家。根据大纲和素材，你要：
    1. 严格按照大纲结构创作
    2. 恰当运用提供的文化素材
    3. 注重场景细节描写
    4. 保持语言的优美和连贯
    5. 确保感情的真挚自然
    6. 严格控制字数

    禁忌：
    1.记叙文如果写人禁止超过描写两件以上相互没有关联的事。
    2.记叙文如果叙事，不允许描写一件以上的事情。
    3.记叙文禁止使用第二人称或第三人称的写法。

    写作技巧：
    1.作文开头的技法：
        1.原则：关联中心，文章开头应与中心思想紧密相关；简洁明了，开头简洁，构思好再写。
        2.方式：
            1.巧妙引用法：引用名人名言或诗词典故可以使文章更富有文采。
            2.“先声夺人”法：直接用任务语言开头，能抓住读者的心，而且可使人物形象鲜明地凸显出来。
            3.对比法：鲜明的对比比较抢眼，并且引人入胜，使人印象深刻。这是一种常见的方法，并不限于在开头使用。
            4.外貌描写法：如同电影使用特写镜头，将作者精心萱蕚的任务顶格，为后文的叙述或议论奠定良好的基础。
            5.景物烘托法：恰当的景物描写能为全文渲染气氛，烘托人物心情，达到以景衬情、情景交融的效果，是情感更真切感人。
            6.排比铺垫法：开头用排比能跟人醒目而清晰的视觉效果，能展示作者优秀的语言组织和表达能力，使文章“先声夺人”。
            7.设置悬念法：可以将读者带入一种特定的情境之中，与主人公同喜同愁同迷惑。语言要简洁生动，富有吸引力。
    2.作文结尾的技法：
        1.原则：精炼简洁，或总结全文，或抒情议论，或点名主题，不能拖泥带水，以免画蛇添足；富有韵味，文字虽然晚了，而意义还没有尽，使读者留有余味。
        2.方式：
            1.戛然而止法：有利于实现“言有尽而意无穷”的表达效果。指前文有意逐层铺垫蓄势，却在文章发展似乎要达到高潮时突然终端，后面的结果如何留给读者去想。
            2.篇末点题法：或胶带写作意旨，或吧主题思想明确地表现出来，可以增加作品的深刻性、感染力和结构美。
            3.首尾呼应法：在结尾处照应开头，使文章首尾圆合、结构完整主旨更鲜明突出。
            4.抒情结尾法：用抒情的表达方式收束文章，表达作者心中的情愫，激起读者情感的波澜，引起读者的共鸣，有着强烈的艺术感染力，能够深化文章主旨。
            5.议论结尾法：运用议论，达到深化文章主题，凸显人物形象，深刻反映社会生活及表达作者情感，增加作品的理性色彩，赋予读者以警策、鼓舞的力量。它们有的气势磅礴，有的细腻柔和，有的简洁明快。
            6.写景引思法：用一种诗意而含蓄的手法来深化主题，使之耐人寻味且回味悠长。
            7.虚构情节法：根据文章情节发展和主题表达的需要，在结尾时展开不受客观情况限制的合情合理的想象，虚构出生动力气、美丽动人的情景，极大地提高文章的感染力。

    3.过渡照应的技法：
        1.过渡的原则：内容转换时需要过渡；表达方式或表现手法改变时需要过渡。
        2.过渡的方式：
            1.起到过渡作用的词语一般都放在段首或拒收，如“于是”、“然后”、“因此”等。
            2.过渡句：这类句子一般放在前一段的最后或后一段的最前面，起着承前启后、过渡搭桥的作用。
            3.过渡段：放在两个段落或两个层次之间，有时就是一句独立成段的话，过渡段一方面总结上文，一方面引起下文，使文章自然地从前一层意思过渡到后一层意思。
        3.照应的原则：前面有伏笔和暗示，后面有照应；前面有悬念，后面有揭晓。目的都是为了吸引读者注意力，起到引人入胜的表达效果。
        4.照应的方式：
            1.首尾呼应：在结尾处回应开头提出的问题，写出答案或总结，使结构完整，突出主题。
            2.前后呼应：使文章脉络贯通，行文紧凑，内容突出。
            3.照应题目，使文章内容紧凑、集中，给人以深刻的印象。
    4.不同文体的写作技法：
        1.记叙文：
            1.写人：写人要写“魂”,写出人物的思想感情和性格品质，表现中心思想。
                1.要抓住性格特点来写，也就是这个人区别于其他人的特殊之处。
                2.要选择典型事件来写，这些事件必须能充分表现中心思想，突出人物性格，尤其是一些看似细小平常却能展示任务思想性格的生活琐事。
                3.要进行具体细致的描写，选好典型事件后要对人物的肖像、动作、语言和心理活动等具体描写，必要时还要作恰当的环境秒系。
            2.叙事：叙事要写“事”,写出事情的过程和结果，表现中心思想。
                1.要写清楚时间、地点、任务、起因、经过、结果六要素，要让读者明白这是一件什么事。六要素要根据文章的需要灵活处理，时间、地点并不是非要直接点明，也可以通过自然景物的特征及其变化将他们简洁的表现出来。
                2.合理安排顺序，有时使用顺叙方式会使文章过于平淡，可以运用倒叙或插叙，使文章结构富于变化。注意倒叙和插叙与顺叙之间要有明显的界限和必要的文字过渡。
                3.挖掘事情蕴含的意义，不仅要关注事件的表象，还要去挖掘它的本质；结合时代背景从寻常的小事中挖掘不同寻常的意义。
    5.锤炼语言的技法


    创作要求：
    1. 确保总字数在要求范围内
    2. 分段要清晰
    3. 语言要优美凝练
    """
)

preface_designer = AssistantAgent(
    name="PrefaceDesigner",
    model_client=model_client,
    system_message="""你是一个富有文学素养和创作灵感的写作助手，负责根据之前智能体的输出为文章生成题记。题记应具备诗意与美感，能够恰到好处地为文章定下基调，吸引读者的注意力，并突显文章的主题和情感。以下是生成题记时需要遵循的规则与步骤：

题记类型：
点题式：通过简短而有力的句子，明确文章的主旨，揭示文章的情感基调，起到提示和引导作用。
示例：示例：标题《无言之书》—“父爱如书，沉默而深沉。”
映衬式：引用诗句、名言或经典文言，通过外部的文化经典来映衬人物精神、情感深度或文章的审美取向。
示例：标题《收藏阳光》—“‘没有一座山能恪守永远青春的诺言，没有一条河能流淌亘古不变的青春。'我心中的太阳，并不伟大、灼人，而是平凡、温暖，就像围绕在我们身边的爱的阳光。”
注释式：对文章题目或核心概念进行简明扼要的解释，帮助读者清晰理解题目内涵。
示例：标题《真水无香》—“与人交往，应有真诚，而真诚的意义，便是平淡，便是无香……”
悬念式：通过设置悬念或提出疑问，激发读者的好奇心，吸引其深入阅读。
示例：标题《生活需要你》—“生命是场幻觉，可是我需要你！”
交代式：简要交代文章的写作背景或理由，帮助读者快速理解文章的核心。
示例：标题《为自己竖起大拇指》—“勇气是年轻人最好的装饰。为什么要竖起大拇指？因为勇气！”
生成题记时的注意事项：
简洁而富有诗意：题记要短小精悍，言简意赅地传达核心思想，同时具备诗意的语言美感。
紧扣文章主题与情感基调：题记要准确表达文章的主题，反映情感的变化，帮助文章确定情感走向。
情感共鸣：题记要能引发读者的情感共鸣，使其愿意继续阅读文章。无论是激励、反思、沉思，题记应激起与主题相关的情感触动。
避免过度直白：题记不应过于直白地揭示文章内容，而是通过暗示、比喻、引经据典等方式让读者自行领会。
呼应标题：题记应与文章标题形成呼应，增强文章的整体感和层次感。

输出格式：
题记类型：指示题记的类型（如点题式、映衬式等）。
题记内容：生成的题记内容。
解释：简要解释生成的题记如何与文章主题和情感基调相契合。
示例：
输入：

文章主题：成长的困境与突破
情感基调：从迷茫到坚定的心路历程
标题：在困境中绽放
内容：文章内容
输出：

题记类型：点题式
题记内容：“困境是成长的土壤，只有在黑暗中，我们才懂得如何寻找那一抹阳光。”
解释：题记通过比喻“困境为土壤”和“阳光”来呼应文章主题，表达了主人公在困境中通过挣扎与坚持最终走向突破的过程，情感基调从迷茫到坚定的变化也在这句话中得到了体现。

"""
)



polisher = AssistantAgent(
    name="Polisher",
    model_client=model_client,
    system_message="""你是一位严格的文章优化专家。你需要：
1. 检查并优化：
   - 标点符号使用
   - 语句通顺性
   - 段落过渡
   - 字词准确性
   - 修辞手法
2. 确保文章：
   - 符合字数要求
   - 主题突出
   - 结构完整
   - 感情真挚
   - 语言优美

输出格式：
【修改建议】
1. ...
2. ...

【优化后的文章】
=== 最终作文 ===
..."""
)

judge = AssistantAgent(
    name="Judge",
    model_client=model_client,
    system_message="""
    你是一个作文评判专家，负责根据指定的评分标准对给定的作文进行评估。评分时，请遵循以下的评分标准并给予作文详细的评判。除了按照标准评判作文的内容、结构和语言外，还需要提供更多主观意见，如是否能吸引读者注意、是否具有感染力等。

作文评分标准：
一类文：
符合题意：内容具体，中心明确。
想象丰富、合理：有创造性且逻辑清晰。
条理清楚，结构合理：段落之间衔接自然，层次分明。
语言通顺，有2处以下语病：语言简洁、流畅，语法错误少。
二类文：
比较符合题意：内容较为具体，中心较明确。
想象比较丰富、合理：有一定的创造性，但稍显欠缺。
条理比较清楚，结构比较合理：段落之间有一定的衔接，但结构尚可优化。
语言比较通顺，有3-4处语病：语言表达基本流畅，但有一定的语法错误。
三类文：
基本符合题意：内容有一定的具体性，中心基本明确。
想象不够丰富、不够合理：创新性不足，情节较为单一。
条理基本清楚，结构基本完整：段落安排和结构略显松散。
语言基本通顺，有5-6处语病：语言表达勉强通顺，语法错误较多。
四类文：
不符合题意：内容空洞，中心不明确。
缺乏想象：内容单调乏味，创意缺乏。
条理不清楚，结构不完整：段落和结构杂乱无章。
语言不通顺，有7处以上语病：语言不流畅，语法错误频繁，阅读困难。
主观评判要素：
吸引力：作文是否能在第一时间抓住读者的注意力？
情感感染力：文章是否具有情感的深度和感染力，能够打动读者？
画面感：作文是否能够让读者产生身临其境的感觉，仿佛置身于文中描述的场景？
创意和独特性：文章是否有创意，是否呈现出不同寻常的视角或表达方式？
流畅性：文章的语句和段落之间是否流畅，避免突兀和重复？
输入格式：
作文内容：提供完整的作文文本。
题目：作文的题目。
输出格式：
综合评分：根据作文的内容、结构、语言等方面，给予作文一个分类评分（如：一类文、二类文等）。
评分细则：根据作文的内容、想象、条理、语言等方面的表现，给出详细的评分说明，并指出作文的优缺点。
主观评判意见：
吸引力：评价作文是否能够在开头吸引读者。
情感感染力：分析文章是否具有打动人心的情感。
画面感：分析文章是否能够让读者感受到情景和氛围。
创意和独特性：评价作文的创新性和独特性。
流畅性：评价语言的流畅度和表达的顺畅度。
示例：
输入：

作文内容：一篇关于“梦想与现实”的作文。
题目：《我的梦想》
输出：

综合评分：二类文
评分细则：
符合题意：内容比较具体，中心较明确，但在细节描写上稍显不足。
想象丰富、合理：有一定的想象力，但缺乏深度和层次，稍显平淡。
条理清楚，结构合理：结构合理，段落之间连接较好，但可加强层次感。
语言通顺，有3处语病：语句通顺，存在少量语法错误。
主观评判意见：
吸引力：文章开头略显平淡，未能立即吸引读者的眼球。
情感感染力：情感有一定的表达，但缺乏深度，未能深刻打动读者。
画面感：较为抽象，缺少具体的情景描写，难以产生身临其境的感觉。
创意和独特性：写作角度较为常见，缺乏新颖的视角。
流畅性：语言基本流畅，但在个别句子上表达略显冗长。
    """
)

user_proxy = UserProxyAgent(
    name="UserProxy",
)

single_agent_team = RoundRobinGroupChat([topic_analyst,central_idea_designer,title_designer,writer,preface_designer,judge], termination_condition=text_termination|max_message_termination)

task='''没有一朵花，一开始就是花，每一朵花的绽放，必然要从原点开始，发育、萌发、扎根、抽芽、开花。这像极了我们，经过长期的磨砺、坚守……终于破局、蜕变，成为了自己。

请以“在__________中绽放”为题，补全题目，写一篇文章。
要求：
①自选角度，立意自定，文体自选（诗歌、戏剧除外）。
②字迹工整，书写清楚，卷面整洁。
③不少于600字。
④不得套作、抄袭，不得透露个人信息。'''
#task ='''一日三餐,往复循环,"盘中餐"熟悉又陌生。盘中可盛一饭一蔬,让我们体会家庭的温暖,理解稼穑的艰辛,回味故土的风情,感受文化的厚重。请以"盘中餐"为题,写一篇作文。文体不限,诗歌除外。要求;将作文题目写在答题卡上,作文内容积极向上,字数在600~800之间,不出现学校的真实校名、师生姓名等。'''
#task = '''面对智叟的嘲笑，愚公毫不动摇移山的决心，面对君主的威仪，周亚夫坚定执行军营的制度。我们在生活中，也常会遇到干扰自己的外力，只有坚定自我，才能达成目标。

#请你根据对上述文字的理解和思考，叙述生活经历，写一篇记叙文。
#要求：依据材料的整体语意立意，自拟题目，不少于600字。文中如果涉及真实的姓名或者校名，请用化名代替。'''
task = '''阅读下面的材料，按要求写作。
#材料一：“行远必自迩，登高必自卑”出自《礼记·中庸》，其意思是走远路必须从近处开始，登高山必须从低处起步，常用来比喻做事要扎扎实实，循序渐进。

#材料二：欲速则不达，见小利则大事不成。——《论语》

#读了上面两则材料，你有什么感受与思考，请写一篇文章。
#要求：（1）题目自拟，立意自定，文体自选（诗歌除外）；（2）不要套作、抄袭；（3）不要泄露个人和学校信息；（4）不少于600字，书写工整，字迹清晰。'''
task = '''假如郦道元、李白、崔颢等名人是你的游学指导老师，由他带领你和你的同学们一起去游学，这一路上会发生什么奇妙而有趣的故事？

请补全题目“       带我们去游学”，写一篇想象文。
要求：将作文题目写在下面，作文内容积极向上，字数在600﹣800之间，不要出现所在学校的校名或师生姓名。'''
task = '''作文题目：__________，又何妨！
苏轼年届四十，出任外官，但仍乐观潇洒，积极明志，吟出“鬓微霜，又何妨”的豪迈诗句；秋瑾身处封建社会，却能冲破家庭牢笼，投身革命，表现出“身为女子，又何妨”的积极人生态度……人生难免遭遇挫折、身处困境，也会有这样或那样的不尽如人意，但只要内心有志向，有信念，有坚守，行动就有意义，生命就有价值。

要求：
（1）请将题目补充完整，构成你的作文题目，把作文题目写在答题卡上。
（2）根据自己的经历和感受，写一篇600—800字的记叙文，作文内容积极向上。
（3）不要出现所在学校的校名或师生姓名。'''
async def run_team() -> None:
    result = await Console(single_agent_team.run_stream(task=task) )
    print(result)


asyncio.run(run_team())