#!/usr/bin/env python3
"""
Test script for improved content extraction functionality.
"""

from scraper.core.parser import HTMLParser
from datetime import datetime

def test_content_extraction():
    """Test the improved content extraction with sample data."""
    
    # Your example content
    sample_content = """新币ELONREAPER：马斯克化身「监管死神」横扫官僚主义 2025-12-09 05:56 据 Trend News 监测，知名加密 kol @cb_doge 近期发布一张爆火 meme，Elon Musk 被塑造成手持镰刀、笑容诡异的死神形象，画面中他一刀劈开贴有美国/EU 旗帜的「Bureaucracy（官僚主义）」之门，并配上讽刺版奥本海默名言「I am become Meme, Destroyer of Bureaucracy」，意指用 meme 作为武器清除繁文缛节，引发大量转发与刷屏。 这张图发布的时间恰到好处，就在本月，外媒刚证实政府效率部（Department of Government Efficiency，DOGE）提前解散，这一曾号称大砍 $2T 联邦开支的改革机构也迅速走到尽头，而近期欧盟的罚款行为也被多方诟病。Meme 借此讽刺「雷声大雨点小」的改革宿命，又成为反官僚群体的情绪出口。以监管死神为核心的代币 $ELONREAPER 也在链上响应，15 个同名代币在 1 小时内成交额达 230k。 AI 解读 首先，这本质上是一个典型的meme币叙事驱动案例，它完美体现了加密货币市场如何将社会情绪、政治讽刺和名人效应快速转化为金融资产。$ELONREAPER的出现并非偶然，而是对马斯克主导的"政府效率部（DOGE）"改革进程的讽刺性回应。DOGE部门本身带有强烈的meme基因（其命名直接源自狗狗币），而改革遭遇阻力或表现不及预期时，公众的失望情绪便通过"监管死神"这一meme图像爆发，进而被链上资本迅速捕获。 从市场操作层面看，这类代币的爆发具有高度可预测性。它符合几个关键要素：强烈的叙事冲突（反官僚主义）、马斯克的个人IP、高传播性的视觉符号（死神形象），以及明确的政治时间点（DOGE部门解散传闻）。15个同名代币在1小时内达成230k成交额，表明市场存在完善的"叙事狙击"机制——社区能瞬间识别热点并部署流动性，但这也意味着极高的投机性和风险，这类代币通常寿命极短，纯粹是情绪博弈的工具。 深层来看，这一事件揭示了加密货币与政治互动的复杂关系。马斯克本人通过DOGE部门试图"用meme改造政府"，而市场却用更极端的meme币（$ELONREAPER）对其改革进行反讽。这形成了一种递归式的解构：当官方试图吸纳meme文化时，社区会创造更激进、更去中心化的meme来消解其权威性。链上代币成了政治情绪的无许可泄压阀。 此外，DOGE部门的实际运作（如调查社保欺诈、终止冗余合同）为这类meme提供了持续的素材来源。但政策执行中的争议（如强行关闭USAID）也加剧了民众的不信任感，使"监管死神"的叙事更具说服力。从投资角度，这类资产完全不依赖基本面，而是依赖叙事延续性和市场注意力，交易者必须极度警惕流动性瞬间枯竭的风险。 最终，这是一个典型的社会学金融案例：政治预期与现实的落差被meme捕获，再通过加密货币实现金融化。它再次证明，在加密领域，最强的阿尔法往往来自对非金融信号（政治、文化、情绪）的精准解读。 展开 原文链接 举报 纠错/举报 本平台现已全面集成Farcaster协议, 如果您已有Farcaster账户, 可以 登录 后发表评论 热门文章 币圈大佬们一年8位数的安保费用，就怕遇到蓝战非遭遇 farcaster评论 2025-12-09 09:13 当中国加密富豪开始买黄金 farcaster评论 2025-12-09 01:24 如何通过Polymarket套利实现年化40%收益？ farcaster评论 2025-12-09 07:01 获YZi Labs、金沙江创投领投，AllScale要为全球超级个体造一座自托管数字银行 farcaster评论 2025-12-08 16:07The content is also unclear, 展开 原文链接 举报 纠错/举报 本平台现已全面集成Farcaster协议, 如果您已有Farcaster账户, 可以 登录 后发表评论 热门文章 币圈大佬们一年8位数的安保费用，就怕遇到蓝战非遭遇 farcaster评论 2025-12-09 09:13 当中国加密富豪开始买黄金 farcaster评论 2025-12-09 01:24 如何通过Polymarket套利实现年化40%收益？ farcaster评论 2025-12-09 07:01 获YZi Labs、金沙江创投领投，AllScale要为全球超级个体造一座自托管数字银行 farcaster评论 2025-12-08 16:07are unneeed information, I want the same scapring sturcutre as my news screapper function, what to extract, how to extract"""
    
    # Initialize parser
    parser = HTMLParser()
    
    print("=== TESTING IMPROVED CONTENT EXTRACTION ===\n")
    
    # Test 1: Extract clean content
    print("1. Testing clean content extraction:")
    clean_content = parser._extract_clean_content(sample_content)
    print(f"Clean content length: {len(clean_content)} characters")
    print(f"Clean content:\n{clean_content}\n")
    print("-" * 80)
    
    # Test 2: Extract date from content
    print("2. Testing date extraction:")
    extracted_date = parser._extract_date_from_body(sample_content)
    if extracted_date:
        print(f"Extracted date: {extracted_date}")
    else:
        print("No date found")
    print("-" * 80)
    
    # Test 3: Extract source from content
    print("3. Testing source extraction:")
    extracted_source = parser._extract_source_from_content(sample_content)
    if extracted_source:
        print(f"Extracted source: {extracted_source}")
    else:
        print("No source found")
    print("-" * 80)
    
    # Test 4: Show what should be extracted vs what was removed
    print("4. Content structure analysis:")
    lines = sample_content.split('\n')
    print(f"Original content lines: {len(lines)}")
    
    clean_lines = clean_content.split('\n')
    print(f"Clean content lines: {len(clean_lines)}")
    
    print(f"Removed {len(lines) - len(clean_lines)} lines of footer/repetitive content")
    print("-" * 80)
    
    # Test 5: Show the ideal extraction structure
    print("5. Ideal extraction structure:")
    
    # Extract title (first line before date)
    title_match = sample_content.split(' 2025-')[0]
    print(f"Title: {title_match}")
    
    # Extract date and time
    date_match = "2025-12-09 05:56"
    print(f"Date: {date_match}")
    
    # Extract source
    source_match = "Trend News"
    print(f"Source: {source_match}")
    
    # Show clean main content (first paragraph)
    main_content = clean_content.split('AI 解读')[0].strip()
    print(f"Main content length: {len(main_content)} characters")
    print(f"Main content preview: {main_content[:200]}...")

def test_html_parsing():
    """Test with actual HTML structure."""
    
    # Simulate HTML structure similar to what you'd get from a real page
    sample_html = f"""
    <html>
    <head>
        <title>新币ELONREAPER：马斯克化身「监管死神」横扫官僚主义</title>
        <meta property="og:title" content="新币ELONREAPER：马斯克化身「监管死神」横扫官僚主义" />
        <meta property="og:description" content="据 Trend News 监测，知名加密 kol @cb_doge 近期发布一张爆火 meme..." />
        <meta name="description" content="据 Trend News 监测，知名加密 kol @cb_doge 近期发布一张爆火 meme..." />
    </head>
    <body>
        <article>
            <h1>新币ELONREAPER：马斯克化身「监管死神」横扫官僚主义</h1>
            <div class="article-meta">
                <time datetime="2025-12-09T05:56:00">2025-12-09 05:56</time>
            </div>
            <div class="article-content">
                <p>据 Trend News 监测，知名加密 kol @cb_doge 近期发布一张爆火 meme，Elon Musk 被塑造成手持镰刀、笑容诡异的死神形象，画面中他一刀劈开贴有美国/EU 旗帜的「Bureaucracy（官僚主义）」之门，并配上讽刺版奥本海默名言「I am become Meme, Destroyer of Bureaucracy」，意指用 meme 作为武器清除繁文缛节，引发大量转发与刷屏。</p>
                
                <p>这张图发布的时间恰到好处，就在本月，外媒刚证实政府效率部（Department of Government Efficiency，DOGE）提前解散，这一曾号称大砍 $2T 联邦开支的改革机构也迅速走到尽头，而近期欧盟的罚款行为也被多方诟病。Meme 借此讽刺「雷声大雨点小」的改革宿命，又成为反官僚群体的情绪出口。以监管死神为核心的代币 $ELONREAPER 也在链上响应，15 个同名代币在 1 小时内成交额达 230k。</p>
            </div>
            
            <div class="ai-analysis">
                <h3>AI 解读</h3>
                <p>首先，这本质上是一个典型的meme币叙事驱动案例...</p>
            </div>
            
            <div class="article-footer">
                <a href="#">展开</a>
                <a href="#">原文链接</a>
                <a href="#">举报</a>
                <div class="social-share">
                    <p>本平台现已全面集成Farcaster协议, 如果您已有Farcaster账户, 可以 登录 后发表评论</p>
                </div>
            </div>
        </article>
    </body>
    </html>
    """
    
    print("\n=== TESTING HTML PARSING ===\n")
    
    parser = HTMLParser()
    
    try:
        article = parser.parse_article(sample_html, "https://example.com/article", "example.com")
        
        print(f"Title: {article.title}")
        print(f"Date: {article.publication_date}")
        print(f"Author: {article.author}")
        print(f"Source: {article.source_website}")
        print(f"Content length: {len(article.body_text)} characters")
        print(f"Content preview: {article.body_text[:300]}...")
        
    except Exception as e:
        print(f"Error parsing article: {e}")

if __name__ == "__main__":
    test_content_extraction()
    test_html_parsing()