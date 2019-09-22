import sys
import bs4
import logging
from bs4 import BeautifulSoup

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


class XPath:

    @staticmethod
    def get_soup(file: str) -> BeautifulSoup:
        f = open(file)
        soup = BeautifulSoup(f, features="lxml")
        f.close()
        return soup

    @staticmethod
    def compare(origin: dict, other: dict) -> bool:
        return origin["text"].lower().strip() == other["text"].lower().strip() or origin["attrs"].get("id") and \
                origin["attrs"]["id"] == other["attrs"].get("id") or \
                origin["attrs"].get("class") and \
                origin["attrs"]["class"] == other["attrs"].get("class")

    def look_for_children_or_result(self, child: bs4.element.Tag, origin: dict) -> dict or None:
        try:
            other = {"attrs": child.attrs, "text": child.text}
            if self.compare(origin, other):
                return {"result": child}
            else:
                return {"child_list": list(child.children)}
        except AttributeError:
            return None

    def look_for_result(self, button_parent: bs4.element.Tag, button_origin: dict):
        button_in = list(button_parent.children)
        result = None
        while not result and button_in:
            child_list = []
            # next look for button in list of child or deeper
            for child in button_in:
                if self.look_for_children_or_result(child, button_origin) is None:
                    continue
                elif self.look_for_children_or_result(child, button_origin).get("result"):
                    result = self.look_for_children_or_result(child, button_origin)["result"]
                    return result
                else:
                    child_list.append(self.look_for_children_or_result(child, button_origin)["child_list"])

            button_in = child_list
        return None

    def find_element(self, origin_file: str, other_file: str,
                     id_name: str = "make-everything-ok-button") -> dict or None:
        soup = self.get_soup(origin_file)
        soup_other = self.get_soup(other_file)

        # find attrs and text of original button
        button = soup.find(id=id_name)
        button_origin = {"attrs": button.attrs, "text": button.text}

        # find list of patents for original button
        path = []
        parents_origin = list(button.parents)
        for parent in parents_origin:
            path.append((parent.name, parent.attrs))

        # look for first parent of original button that we have in other document as well
        result = None
        for parent in path:
            button_parent = soup_other.find_all(attrs=parent[1])
            if button_parent:
                # look for list of children for that element
                for item in button_parent:
                    result = self.look_for_result(item, button_origin)
                    if result:
                        logging.info(f"element was found in the new file: {result}")
                        return result
        return result

    @staticmethod
    def xpath(element: bs4.element.Tag) -> str:
        tags = []
        child = element if element.name else element.parent
        for parent in child.parents:
            siblings = parent.find_all(child.name, recursive=False)
            tags.append(
                child.name if 1 == len(siblings) else '%s[%d]' % (
                    child.name,
                    next(i for i, s in enumerate(siblings, 1) if s is child)
                )
            )
            child = parent
            tags.reverse()
        return '/%s' % '/'.join(tags)


def run():
    element = XPath().find_element(origin_file=sys.argv[1], other_file=sys.argv[2])
    path = XPath.xpath(element)
    logging.info(f"XPath:: {path}")
    return path


print(f"button: {run()}")

#sys.argv[1], sys.argv[2]
#'/home/lyudmyla/work/test/xml_analyzer/startbootstrap-sb-admin-2-examples/sample-0-origin.html'
#'/home/lyudmyla/work/test/xml_analyzer/startbootstrap-sb-admin-2-examples/sample-3-the-escape.html'