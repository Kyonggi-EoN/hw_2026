from html.parser import HTMLParser
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PublicationTableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables = {}
        self.image_sources = []
        self._table_id = None
        self._row = None
        self._cell = None
        self._caption = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "img":
            self.image_sources.append(attributes.get("src", ""))
        if tag == "table" and attributes.get("id"):
            self._table_id = attributes["id"]
            self.tables[self._table_id] = {"caption": "", "rows": []}
        elif self._table_id and tag == "caption":
            self._caption = []
        elif self._table_id and tag == "tr":
            self._row = []
        elif self._row is not None and tag in {"th", "td"}:
            self._cell = []

    def handle_data(self, data):
        if self._cell is not None:
            self._cell.append(data)
        elif self._caption is not None:
            self._caption.append(data)

    def handle_endtag(self, tag):
        if self._table_id and tag in {"th", "td"} and self._cell is not None:
            self._row.append(" ".join("".join(self._cell).split()))
            self._cell = None
        elif self._table_id and tag == "tr" and self._row is not None:
            if self._row:
                self.tables[self._table_id]["rows"].append(self._row)
            self._row = None
        elif self._table_id and tag == "caption" and self._caption is not None:
            self.tables[self._table_id]["caption"] = " ".join(
                "".join(self._caption).split()
            )
            self._caption = None
        elif tag == "table" and self._table_id:
            self._table_id = None


class PublicationTableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        parser = PublicationTableParser()
        parser.feed((ROOT / "index.html").read_text(encoding="utf-8"))
        cls.tables = parser.tables
        cls.image_sources = parser.image_sources

    def assert_table(self, table_id, caption, rows):
        self.assertIn(table_id, self.tables)
        self.assertEqual(caption, self.tables[table_id]["caption"])
        self.assertEqual(rows, self.tables[table_id]["rows"])

    def test_inverter_dc_table_preserves_source_values(self):
        self.assert_table(
            "table-inverter-dc",
            "Table 1. β별 인버터 DC 성능 요약",
            [
                ["β", "Driver W/L", "Load W/L", "VM (V)", "Max. gain (V/V)", "VOH (V)", "VOL (V)", "NML (V)", "NMH (V)", "Max. static power (μW)"],
                ["4.00", "15/5", "15/20", "4.183", "1.622", "9.564", "1.436", "−0.351", "4.351", "1.685"],
                ["5.71", "30/7", "15/20", "3.898", "1.987", "9.506", "0.909", "−0.086", "4.512", "1.952"],
                ["8.00", "30/5", "15/20", "3.725", "2.224", "9.410", "0.802", "+0.024", "4.654", "2.008"],
            ],
        )

    def test_geometry_scaling_table_preserves_source_values(self):
        self.assert_table(
            "table-geometry-scaling",
            "Table 2. 폭 / 길이 분할별 요약",
            [
                ["Split", "W (μm)", "L (μm)", "Contact (μm)", "VTH (V)", "Ion (nA)", "Ion/W (nA μm−1)", "IonL (nA μm)", "gm,max (nS)", "Ron (MΩ)", "ID at 10/10 V (nA)"],
                ["Width", "15", "10", "10.0", "2.705", "31.667", "2.111", "—", "13.831", "12.181", "369.344"],
                ["Width", "20", "10", "10.0", "2.705", "42.222", "2.111", "—", "18.441", "9.136", "492.458"],
                ["Width", "25", "10", "10.0", "2.705", "52.778", "2.111", "—", "23.052", "7.309", "615.573"],
                ["Length", "15", "5", "10.0", "—", "21.843", "—", "109.215", "—", "—", "196.084"],
                ["Length", "15", "10", "10.0", "—", "31.667", "—", "316.668", "—", "—", "369.344"],
                ["Length", "15", "20", "10.0", "—", "18.857", "—", "377.144", "—", "—", "244.493"],
            ],
        )

    def test_gate_misalignment_table_preserves_source_values(self):
        self.assert_table(
            "table-gate-misalignment",
            "Table 3. 게이트 오정렬별 전기 특성 요약",
            [
                ["Gate offset (μm)", "VTH (V)", "Ion (nA)", "Ion/Ion,0", "gm,max (nS)", "Ron (MΩ)", "VDSAT (V)", "Early voltage (V)"],
                ["−5", "2.344", "23.929", "0.756", "10.612", "27.162", "8.800", "9.125"],
                ["−3", "2.705", "31.667", "1.000", "13.831", "12.181", "5.946", "38.880"],
                ["0", "2.705", "31.667", "1.000", "13.831", "12.181", "5.946", "38.880"],
                ["+3", "2.705", "31.667", "1.000", "13.831", "12.181", "5.946", "38.880"],
                ["+5", "2.321", "21.289", "0.672", "8.734", "29.279", "6.045", "36.037"],
            ],
        )

    def test_publication_table_pngs_are_not_used_as_page_content(self):
        removed_sources = {
            "static/images/pub_tables/Table01_inverter_dc_performance.png",
            "static/images/pub_tables/Table02_tft_geometry_scaling_metrics.png",
            "static/images/pub_tables/Table03_tft_gate_misalignment_metrics.png",
        }
        self.assertTrue(removed_sources.isdisjoint(self.image_sources))


if __name__ == "__main__":
    unittest.main()
