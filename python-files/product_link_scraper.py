import requests
    from bs4 import BeautifulSoup
    import re
    import os
    from urllib.parse import urljoin, urlparse

    class ProductLinkScraper:
        def __init__(self):
            # 设置默认的用户代理，模拟浏览器访问
            self.headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            # 存储已抓取的链接，避免重复
            self.scraped_links = set()
            # 存储产品链接
            self.product_links = set()

        def is_valid_url(self, url):
            """检查URL是否有效"""
            try:
                result = urlparse(url)
                return all([result.scheme, result.netloc])
            except:
                return False

        def is_product_link(self, url, keywords=None):
            """判断链接是否为产品链接"""
            if not keywords:
                # 默认的产品链接关键词
                keywords = ['product', 'item', 'goods', 'shop', 'buy', 'p/', 'product_id']
            
            # 检查URL中是否包含产品相关关键词
            url_lower = url.lower()
            return any(keyword in url_lower for keyword in keywords)

        def scrape_links(self, url, depth=1, current_depth=1, product_keywords=None):
            """
            抓取网页中的链接
            
            参数:
                url: 要抓取的网页URL
                depth: 抓取深度，1表示只抓取当前页面，2表示抓取当前页面及链接页面等
                current_depth: 当前抓取深度
                product_keywords: 判断产品链接的关键词列表
            """
            if current_depth > depth or url in self.scraped_links:
                return

            print(f"正在抓取: {url} (深度: {current_depth})")
            self.scraped_links.add(url)

            try:
                # 发送请求获取网页内容
                response = requests.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()  # 如果请求失败，抛出异常
            except Exception as e:
                print(f"抓取 {url} 失败: {str(e)}")
                return

            # 解析网页内容
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取所有链接
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                # 转换为绝对URL
                absolute_url = urljoin(url, href)
                
                # 检查是否为有效URL且属于同一个网站
                if self.is_valid_url(absolute_url) and urlparse(absolute_url).netloc == urlparse(url).netloc:
                    # 判断是否为产品链接
                    if self.is_product_link(absolute_url, product_keywords):
                        self.product_links.add(absolute_url)
                        print(f"发现产品链接: {absolute_url}")
                    
                    # 如果还没达到最大深度，继续抓取
                    if current_depth < depth:
                        self.scrape_links(absolute_url, depth, current_depth + 1, product_keywords)

        def save_links_to_file(self, filename='product_links.txt'):
            """将产品链接保存到文件"""
            if not self.product_links:
                print("没有找到产品链接")
                return

            with open(filename, 'w', encoding='utf-8') as f:
                for link in sorted(self.product_links):
                    f.write(link + '\n')
            
            print(f"已将 {len(self.product_links)} 个产品链接保存到 {filename}")

        def run(self):
            """运行抓取工具"""
            print("===== 产品链接抓取工具 =====")
            url = input("请输入要抓取的网站URL: ").strip()
            
            if not self.is_valid_url(url):
                print("无效的URL，请重新输入")
                return
            
            try:
                depth = int(input("请输入抓取深度 (1-3，数字越大抓取越多页面): ").strip())
                depth = max(1, min(3, depth))  # 限制深度在1-3之间
            except ValueError:
                depth = 1
                print("使用默认抓取深度: 1")
            
            custom_keywords = input("请输入产品链接关键词(用逗号分隔，不输入则使用默认): ").strip()
            product_keywords = None
            if custom_keywords:
                product_keywords = [kw.strip().lower() for kw in custom_keywords.split(',')]
            
            print("\n开始抓取...")
            self.scrape_links(url, depth, product_keywords=product_keywords)
            
            # 保存结果
            self.save_links_to_file()
            
            print("\n抓取完成!")

    if __name__ == "__main__":
        scraper = ProductLinkScraper()
        scraper.run()
    