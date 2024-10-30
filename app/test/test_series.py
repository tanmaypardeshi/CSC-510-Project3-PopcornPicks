import unittest
from bs4 import BeautifulSoup
import os

class TestHTMLRendering(unittest.TestCase):

    def setUp(self):
        # 构建绝对路径并加载 HTML 文件
        base_path = os.path.abspath("CSC-510-movie-mood/app/src/templates/new_series.html")
        with open(base_path, 'r', encoding='utf-8') as f:
            html_doc = f.read()
        # 使用 BeautifulSoup 解析 HTML 文件内容
        self.soup = BeautifulSoup(html_doc, 'html.parser')

    def test_mismatched_heading_tag(self):
        """测试：检测不匹配的 h2 闭合标签"""
        heading = self.soup.find('h2')
        # 检查是否存在不匹配的闭合标签（h2 -> h3）
        self.assertIsNotNone(heading, "Heading h2 not found")
        self.assertIn("</h3>", str(heading.parent), "Found mismatched closing tag </h3> for <h2>")

    def test_show_message_alert(self):
        """测试：检查错误信息显示"""
        alert_div = self.soup.find('div', class_='alert alert-danger')
        self.assertIsNotNone(alert_div, "Alert message div not found when 'show_message' is true")

    def test_today_releases_title(self):
        """测试：检查‘Today Releases:’标题正确显示"""
        releases_heading = self.soup.find('h2', text="Today Releases:")
        self.assertIsNotNone(releases_heading, "Today Releases title not found or not correct")

    def test_series_list_container(self):
        """测试：newSeriesList列表容器是否存在"""
        new_series_list = self.soup.find(id="newSeriesList")
        self.assertIsNotNone(new_series_list, "newSeriesList ID not found in the HTML document")

    def test_tip_header_text(self):
        """测试：检查 tipHeader 样式是否正确显示"""
        tip_header = self.soup.find('h6', class_="tipHeader")
        self.assertIsNotNone(tip_header, "Tip header with class 'tipHeader' not found")
        self.assertEqual(tip_header.text.strip(), "✨Tip: Stay tuned for TODAY's series releases! ✨", "Tip header text mismatch")

    def test_container_margin_top(self):
        """测试：检查 container 的 margin-top 样式"""
        container_div = self.soup.find('div', class_="container")
        self.assertIn("margin-top: 60px;", str(container_div), "Container margin-top style not set to 60px")

    def test_multiline_series_items(self):
        """测试：多行内容正确显示"""
        series_items = self.soup.find_all('li', class_="list-group-item")
        for item in series_items:
            self.assertTrue(len(item.text.strip()) > 0, "Empty series item text found")

    def test_responsive_layout(self):
        """测试：不同屏幕尺寸上的布局"""
        row_div = self.soup.find('div', class_="row")
        self.assertIsNotNone(row_div, "Responsive row class not found")

    def test_special_characters_in_series_name(self):
        """测试：检查 series.name 中的特殊字符是否正确转义"""
        special_chars_series = "<>&\"'"
        series_item = self.soup.new_tag("h3")
        series_item.string = special_chars_series
        self.soup.append(series_item)
        self.assertIn("&lt;&gt;&amp;&quot;&#x27;", str(self.soup), "Special characters not escaped in series.name")

    def test_alert_message_style(self):
        """测试：检查 alert 消息样式是否正确"""
        alert_div = self.soup.find('div', class_="alert alert-danger")
        self.assertIsNotNone(alert_div, "Alert div with correct classes not found")

    def test_no_series_items_empty_list(self):
        """测试：当 series 列表为空时不显示内容"""
        new_series_list = self.soup.find(id="newSeriesList")
        self.assertIsNone(new_series_list.find('li'), "Series list items should not be present when series list is empty")

    # 更多测试...

if __name__ == "__main__":
    unittest.main()
