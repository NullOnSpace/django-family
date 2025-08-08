from django.utils.translation import gettext as _

from .models import Member, Relation


class Ancestor:
    member: Member
    degree: int

    def __init__(self, member: Member, degree: int):
        self.member = member
        self.degree = degree


def get_ancestors(member: Member) -> dict[Member, list[Ancestor]]:
    ancestors = {member: [Ancestor(member, 0)]}
    to_visit = [ancestors[member][-1]]
    while True:
        ancestor = to_visit.pop()
        mem = ancestor.member
        degree = ancestor.degree
        for relation in Relation.objects.filter(member2=mem, relation_type='P'):
            if relation.member1 not in ancestors:
                ancestors[relation.member1] = ancestors[mem] + [
                    Ancestor(relation.member1, degree + 1)]
                to_visit.append(ancestors[relation.member1][-1])
        if not to_visit:
            break
    return ancestors


def find_lowest_common_ancestor(member1: Member, member2: Member) -> None | list[list[Ancestor]]:
    ancestors1 = get_ancestors(member1)
    ancestors2 = get_ancestors(member2)
    common_ancestors = ancestors1.keys() & ancestors2.keys()
    if not common_ancestors:
        return None
    lowest_common_ancestor = min(
        common_ancestors, key=lambda x: len(ancestors1[x]))
    return [ancestors1[lowest_common_ancestor], ancestors2[lowest_common_ancestor]]


def calc_blood_relation(member1: Member, member2: Member) -> str:
    """返回 member2 对 member1 的称呼 即1是2的什么什么"""
    ancestors = find_lowest_common_ancestor(member1, member2)
    if ancestors is None:
        return _('No relationship')
    ancestors1, ancestors2 = ancestors
    reverse = False
    # 令 2 的祖先链长度总是 >= 1 即 1 的辈分 >= 2
    # 在根据reverse决定是否反找关系
    if len(ancestors1) > len(ancestors2):
        ancestors1, ancestors2 = ancestors2, ancestors1
        reverse = True
    match len(ancestors2) - len(ancestors1):
        case 0:
            if member1 == member2:
                return "自己"
            else:
                gender = ancestors1[0].member.gender
                if gender == "M":
                    rel = "兄弟"
                elif gender == "F":
                    rel = "姐妹"
                else:
                    rel = "胞亲"
                if all(map(lambda x: x.member.gender == "M", ancestors1[1:] + ancestors2[1:])):
                    prefix = "堂"
                else:
                    prefix = "表"
                return f"{prefix}{rel}"
        case 1:
            is_parent = ancestors2[1].member == ancestors1[0].member
            if is_parent:
                return "父母与子女"
            else:
                if ancestors2[1].member.gender == 'M':
                    # 姨舅
                    return "姨" if ancestors1[0].member.gender == 'M' else "舅"
                else:
                    # 叔伯姑
                    return "叔伯" if ancestors1[0].member.gender == 'F' else "姑"
                
        case 2:
            return _('Grandparent')
        case 3:
            return _('Great-grandparent')
        case _:
            return f"意料外的辈分差: \n{ancestors1}\n{ancestors2}"
