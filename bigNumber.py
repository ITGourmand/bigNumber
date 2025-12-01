import re

SUFFIXES = ["", "k", "M", "B", "T", "Qa", "Qt", "Sx", "Sp", "Oc", "No"]

def kill(e=""):
    if e:
        print(e)
    raise SystemExit

def index_to_suffix(n):
    negative = n < 0
    n = abs(n)
    if n < len(SUFFIXES):
        suf = SUFFIXES[n]
    else:
        n -= len(SUFFIXES)
        n += 26
        letters = []
        while n >= 0:
            n, r = divmod(n, 26)
            letters.append(chr(97 + r))
            n -= 1
        suf = "".join(reversed(letters))
    if negative:
        suf = "!" + suf
    return suf


def suffix_to_index(s):
    if not s:
        return 0
    negative = False
    if s[0] == '!':
        negative = True
        s = s[1:]
    if s in SUFFIXES:
        idx = SUFFIXES.index(s)
    else:
        n = 0
        for c in s:
            if not ord("a") <= ord(c) <= ord("z") or len(s) == 1:
                kill(f"Suffixe {c} is incorrect")
            n = n * 26 + (ord(c) - 97 + 1)
        idx = n + len(SUFFIXES) - 27
    return -idx if negative else idx

def normalize_blocks(b):
    if not b:
        return b
    while True:
        changed = False
        for e in sorted(list(b.keys())):
            val = b.get(e, 0)
            if val >= 1000:
                carry, rem = divmod(val, 1000)
                b[e] = rem
                b[e + 1] = b.get(e + 1, 0) + carry
                changed = True
            elif val < 0:
                borrow = (-val + 999) // 1000
                b[e] += borrow * 1000
                b[e + 1] = b.get(e + 1, 0) - borrow
                changed = True
        if not changed:
            break
    for e in list(b.keys()):
        if b[e] == 0:
            del b[e]
    return b

def parse_number_to_blocks(s):
    match = re.fullmatch(r'([+\-]?)([0-9]*\.?[0-9]+)([!a-zA-Z]+)?', s)
    if not match:
        kill(f"Format invalide: {s}")
    sign_str, num_str, suf = match.groups()
    sign = -1 if sign_str == "-" else 1
    exp = suffix_to_index(suf) if suf else 0

    if '.' in num_str:
        int_part, dec_part = num_str.split('.')
    else:
        int_part, dec_part = num_str, ''

    blocks = {}
    if int_part:
        blocks[exp] = int(int_part)

    blocks = normalize_blocks(blocks)

    dec_full = dec_part.ljust(((len(dec_part) + 2) // 3) * 3, '0')
    for i in range(0, len(dec_full), 3):
        chunk = dec_full[i:i + 3]
        blocks[exp - (i // 3 + 1)] = int(chunk)

    return {"sign": sign, "blocks": blocks}



def compare_blocks(a, b):
    """Retourne 1 si a>b, 0 si a==b, -1 si a<b"""
    keys = sorted(set(a.keys()) | set(b.keys()), reverse=True)
    for k in keys:
        av = a.get(k, 0)
        bv = b.get(k, 0)
        if av > bv:
            return 1
        elif av < bv:
            return -1
    return 0

def add_blocks(a, b):
    if a["sign"] == b["sign"]:
        res_blocks = a["blocks"].copy()
        for k, v in b["blocks"].items():
            res_blocks[k] = res_blocks.get(k, 0) + v
        return {"sign": a["sign"], "blocks": normalize_blocks(res_blocks)}
    else:
        cmp = compare_blocks(a["blocks"], b["blocks"])
        if cmp == 0:
            return {"sign": 1, "blocks": {}}
        elif cmp > 0:
            res_blocks = a["blocks"].copy()
            for k, v in b["blocks"].items():
                res_blocks[k] = res_blocks.get(k, 0) - v
            return {"sign": a["sign"], "blocks": normalize_blocks(res_blocks)}
        else:
            res_blocks = b["blocks"].copy()
            for k, v in a["blocks"].items():
                res_blocks[k] = res_blocks.get(k, 0) - v
            return {"sign": b["sign"], "blocks": normalize_blocks(res_blocks)}

def sub_blocks(a, b):
    b_copy = {"sign": -b["sign"], "blocks": b["blocks"].copy()}
    return add_blocks(a, b_copy)

def mul_blocks(a, b):
    sign = a["sign"] * b["sign"]
    res = {}
    for ea, va in a["blocks"].items():
        for eb, vb in b["blocks"].items():
            res[ea + eb] = res.get(ea + eb, 0) + va * vb
    return {"sign": sign, "blocks": normalize_blocks(res)}

def blocks_to_int(b):
    total = 0
    for exp, val in b.items():
        total += val * (10 ** (exp * 3))
    return total

def div_blocks(a, b):
    bi = blocks_to_int(b["blocks"])
    if bi == 0:
        kill("Division par zéro")
    sign = a["sign"] * b["sign"]
    result = {}
    remainder = 0
    for exp in sorted(a["blocks"].keys(), reverse=True):
        val = a["blocks"][exp] + remainder
        q = val // bi
        r = val % bi
        result[exp] = q
        remainder = r * 1000
    exp = min(a["blocks"].keys()) - 1
    while remainder != 0 and exp > -1000:
        q = remainder // bi
        r = remainder % bi
        if q == 0 and r == 0:
            break
        result[exp] = q
        remainder = r * 1000
        exp -= 1
    return {"sign": sign, "blocks": normalize_blocks(result)}

def pow_blocks(base, exponent):
    if exponent < 0:
        kill("Exponent must be positif")
    result = {"sign": 1, "blocks": {0: 1}}
    current = base.copy()

    while exponent > 0:
        if exponent % 2 == 1:  
            result = mul_blocks(result, current)
        current = mul_blocks(current, current) 
        exponent //= 2
    return result

def blocks_to_noncompact(n, min_exp=0):
    if not n["blocks"]:
        return "0"
    blocks = n["blocks"]
    sign = "-" if n["sign"] == -1 else ""
    b = blocks.copy()
    max_exp = max(b.keys())
    main_val = b[max_exp]
    frac_parts = []
    contains_positive_exp = False
    for e in range(max_exp-1, min(b.keys())-1, -1):
        if e >= 0:
            contains_positive_exp = True
        if (contains_positive_exp and min_exp != None) and e < min_exp:
            break
        val = b.get(e,0)
        frac_parts.append(f"{abs(val):03d}")
    frac_str = "".join(frac_parts).rstrip("0")
    if frac_str:
        total_str = f"{main_val}.{frac_str}"
    else:
        total_str = f"{main_val}"
    if max_exp != 0:
        total_str += index_to_suffix(max_exp)
    return sign + total_str

def blocks_to_compact(n, min_exp=0):
    if not n["blocks"]:
        return "0"
    blocks = normalize_blocks(n["blocks"].copy())
    sign = n["sign"]
    items = []
    contains_positive_exp = False

    for exp in sorted(blocks.keys(), reverse=True):
        if exp >= 0:
            contains_positive_exp = True
        if (contains_positive_exp and min_exp != None) and exp < min_exp:
            break
        val = blocks[exp]
        if val == 0:
            continue
        val_signed = val * sign

        if not items:
            s = "-" if val_signed < 0 else ""
        else:
            s = "+" if val_signed > 0 else "-"
        abs_val = abs(val_signed)
        if exp == 0:
            items.append(f"{s}{abs_val}")
        else:
            items.append(f"{s}{abs_val}{index_to_suffix(exp)}")
    return "".join(items)


def eval_expr(expr):
    expr = expr.replace(" ", "")
    expr = expr.replace(",", ".")
    expr = expr.replace("^", "**")
    expr = re.sub(r'([0-9]+)([!a-zA-Z]+)?e([0-9]+)([!a-zA-Z]+)?', r'\1\2\*\*\3\4', expr)
    match = re.match(r'\(?([+\-]?)([0-9]+(\.[0-9]+)?)([!a-zA-Z]+)?\)?', expr) and not re.fullmatch(r'([0-9]+[+\-\*/]+[!a-zA-Z]+)', expr) and not re.search(r'([!a-zA-Z]+\.)|(\.[!a-zA-Z]+)|(\.[0-9]+\.)|(\.\.)', expr)
    if not match:
        kill(f"Format invalide: {expr}")
    expr = str(expr).strip()
    if re.match(r'^[+\-]?\d', expr):
        expr = f"(0{expr})"
    expr = re.sub(r'([*/])-(\d+)([!a-zA-Z]+)?', r'\1(-\2\3)', expr)
    expr = re.sub(r'-\(([^()]+)\)', r'(0-1*(\1))', expr)
    expr = re.sub(r'\((?=[+\-])', '(0', expr)
    expr = re.sub(r'\-\+|\+\-', '-', expr)
    expr = re.sub(r'\-\-', '+', expr)

    tokens = re.findall(r'[0-9]*\.?[0-9]+[!a-zA-Z]*|\*\*|[+\-*/()]', expr)
    if not tokens:
        return {"sign":1,"blocks":{}}
    precedence = {"+":1,"-":1,"*":2,"/":2,"**":3}
    associativity = {"+":"L","-":"L","*":"L","/":"L","**":"R"}
    output = []
    ops = []
    def apply_op():
        op = ops.pop()
        b = output.pop()
        a = output.pop()
        if op == "+": output.append(add_blocks(a,b))
        elif op == "-": output.append(sub_blocks(a,b))
        elif op == "*": output.append(mul_blocks(a,b))
        elif op == "/": output.append(div_blocks(a,b))
        elif op == "**": output.append(pow_blocks(a, blocks_to_int(b["blocks"])))
    for token in tokens:
        if re.fullmatch(r'[0-9]*\.?[0-9]+[!a-zA-Z]*', token):
            output.append(parse_number_to_blocks(token))
        elif token in "+-*/**":
            while (ops and ops[-1] in precedence and
                   (precedence[ops[-1]] > precedence[token] or
                   (precedence[ops[-1]] == precedence[token] and associativity[token]=="L"))):
                apply_op()
            ops.append(token)
        elif token == "(": ops.append(token)
        elif token == ")":
            while ops and ops[-1] != "(": apply_op()
            ops.pop()
    while ops: apply_op()
    return output[0]

class bigNumber:
    def __init__(self, expr = "0", compact: bool = False, min_exp: int | None = 0):
        self.expr = eval_expr(str(expr))
        self.compact = compact
        self.min_exp = min_exp
    def __str__(self):
        if self.compact:
            return blocks_to_compact(self.expr, self.min_exp)
        return blocks_to_noncompact(self.expr, self.min_exp)
    def __repr__(self):
        return f"bigNumber(expr = '{self.expr}', compact = '{self.compact}')"
    def __add__(self, other):
        if isinstance(other, (int,float,str,bigNumber)):
            return bigNumber(f"{self}+{other}", self.compact, self.min_exp)
        raise ValueError(f"Cannot add {type(other)}")
    def __sub__(self, other):
        if isinstance(other, (int,float,str,bigNumber)):
            return bigNumber(f"{self}-{other}", self.compact, self.min_exp)
        raise ValueError(f"Cannot sub {type(other)}")
    def __mul__(self, other):
        if isinstance(other, (int,float,str,bigNumber)):
            return bigNumber(f"({self})*{other}", self.compact, self.min_exp)
        raise ValueError(f"Cannot multiply {type(other)}")
    def __truediv__(self, other):
        if isinstance(other, (int,float,str,bigNumber)):
            return bigNumber(f"({self})/{other}", self.compact, self.min_exp)
        raise ValueError(f"Cannot divide {type(other)}")
    def __pow__(self, other):
        if isinstance(other, (int,float,str,bigNumber)):
            return bigNumber(f"({self})**{other}", self.compact, self.min_exp)
        raise ValueError(f"Cannot multiply {type(other)}")
    def __radd__(self, other):
        if isinstance(other, (int,float,str,bigNumber)):
            return bigNumber(f"{other}+{self}", self.compact, self.min_exp)
        raise ValueError(f"Cannot add {type(other)}")
    def __rsub__(self, other):
        if isinstance(other, (int,float,str,bigNumber)):
            return bigNumber(f"{other}-{self}", self.compact, self.min_exp)
        raise ValueError(f"Cannot sub {type(other)}")
    def __rmul__(self, other):
        if isinstance(other, (int,float,str,bigNumber)):
            return bigNumber(f"{other}*({self})", self.compact, self.min_exp)
        raise ValueError(f"Cannot multiply {type(other)}")
    def __rtruediv__(self, other):
        if isinstance(other, (int,float,str,bigNumber)):
            return bigNumber(f"{other}/({self})", self.compact, self.min_exp)
        raise ValueError(f"Cannot divide {type(other)}")
    def __rpow__(self, other):
        if isinstance(other, (int,float,str,bigNumber)):
            return bigNumber(f"({self})**{other}", self.compact, self.min_exp)
        raise ValueError(f"Cannot multiply {type(other)}")
    def __eq__(self, other):
        if isinstance(other, (int,float,str,bigNumber)):
            return str(bigNumber(self,False,None)) == str(bigNumber(other,False,None))
        raise ValueError(f"Cannot compare {type(other)}")

__all__ = ["bigNumber"]

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Évalue des nombres gigantesques.")
    parser.add_argument("expr", help="Expression à calculer")
    parser.add_argument("-c", "--compact", action="store_true", help="Sortie compacte")
    args = parser.parse_args()

    try:
        print(bigNumber(args.expr, compact=args.compact))
    except Exception as e:
        print("Erreur :", e)