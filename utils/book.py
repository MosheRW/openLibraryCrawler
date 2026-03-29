class Book:
    def __init__(self, title: str, author: str, year: int, url: str | None = None):
        self._title = title
        self._author = author
        self._year = year
        self._url = url

    def __repr__(self) -> str:
        return f"Book(title='{self.title}', author='{self.author}', year={self.year}, url='{self.url}')"

    def __str__(self) -> str:
        return f"{self.title} by {self.author} ({self.year}) - {self.url if self.url else 'No URL'}"

    @property
    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "author": self.author,
            "year": self.year,
            "url": self.url
        }

    @property
    def to_json(self) -> str:
        import json
        return json.dumps(self.to_dict)

    @property
    def to_csv(self) -> str:
        import csv
        from io import StringIO
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=self.to_dict.keys())
        writer.writeheader()
        writer.writerow(self.to_dict)
        return output.getvalue()

    @property
    def to_xml(self) -> str:
        from xml.etree.ElementTree import Element, tostring
        book_element = Element("book")
        for key, value in self.to_dict.items():
            child = Element(key)
            child.text = str(value)
            book_element.append(child)
        return tostring(book_element).decode()

    @property
    def to_html(self) -> str:
        return f"<div class='book'><h2>{self.title}</h2><p>Author: {self.author}</p><p>Year: {self.year}</p><p>URL: <a href='{self.url}'>{self.url}</a></p></div>"

    @property
    def to_markdown(self) -> str:
        return f"## {self.title}\n\n- Author: {self.author}\n- Year: {self.year}\n- URL: [{self.url}]({self.url})"

    @property
    def to_yaml(self) -> str:
        import yaml
        return yaml.dump(self.to_dict)

    @property
    def title(self) -> str:
        return self._title

    @property
    def author(self) -> str:
        return self._author

    @property
    def year(self) -> int:
        return self._year

    @property
    def url(self) -> str | None:
        return self._url

    def set_url(self, url: str) -> None:
        self._url = url
