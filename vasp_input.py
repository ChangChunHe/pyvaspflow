from function_toolkit import str_delimited, clean_lines, unlzw
import re
import json
from os import path


class Incar(dict):

    def __init__(self, params=None):
        self.update({'ISIF':2,'ISTART':0,'ICHARG':2,'NSW':50,'IBRION':2,
        'EDIFF':1E-5,'EDIFFG':-0.01,'ISMEAR':0,'NPAR':4,'LREAL':'Auto',
        'LWAVE':'F','LCHARG':'F','ALGO':'All'})
        if params:
            if (params.get("MAGMOM") and isinstance(params["MAGMOM"][0], (int, float))) \
                    and (params.get("LSORBIT") or params.get("LNONCOLLINEAR")):
                val = []
                for i in range(len(params["MAGMOM"])//3):
                    val.append(params["MAGMOM"][i*3:(i+1)*3])
                params["MAGMOM"] = val
            self.update(params)

    def __setitem__(self, key, val):
        super().__setitem__(
            key.strip(), Incar.proc_val(key.strip(), str(val).strip()))

    def as_dict(self):
        d = dict(self)
        d["@module"] = self.__class__.__module__
        d["@class"] = self.__class__.__name__
        return d

    @classmethod
    def from_dict(cls, d):
        if d.get("MAGMOM") and isinstance(d["MAGMOM"][0], dict):
            d["MAGMOM"] = [Magmom.from_dict(m) for m in d["MAGMOM"]]
        return Incar({k: v for k, v in d.items() if k not in ("@module", "@class")})

    def get_string(self, sort_keys=False, pretty=True):

        keys = self.keys()
        if sort_keys:
            keys = sorted(keys)
        lines = []
        for k in keys:
            if k == "MAGMOM" and isinstance(self[k], list):
                value = []
                if (isinstance(self[k][0], list) or isinstance(self[k][0], Magmom)) and \
                        (self.get("LSORBIT") or self.get("LNONCOLLINEAR")):
                    value.append(" ".join(str(i) for j in self[k] for i in j))
                elif self.get("LSORBIT") or self.get("LNONCOLLINEAR"):
                    for m, g in itertools.groupby(self[k]):
                        value.append("3*{}*{}".format(len(tuple(g)), m))
                else:
                    # float() to ensure backwards compatibility between
                    # float magmoms and Magmom objects
                    for m, g in itertools.groupby(self[k], lambda x: float(x)):
                        value.append("{}*{}".format(len(tuple(g)), m))
                lines.append([k, " ".join(value)])
            elif isinstance(self[k], list):
                lines.append([k, " ".join([str(i) for i in self[k]])])
            else:
                lines.append([k, self[k]])

        if pretty:
            return str(tabulate([[l[0], "=", l[1]] for l in lines],
                                tablefmt="plain"))
        else:
            return str_delimited(lines, None, " = ") + "\n"

    def __str__(self):
        return self.get_string(sort_keys=True, pretty=False)

    def write_file(self, filename='INCAR'):
        with open(filename, "wt") as f:
            f.write(self.__str__())

    @staticmethod
    def from_file(filename):
        with open(filename, "r") as f:
            return Incar.from_string(f.read())

    @staticmethod
    def from_string(string):
        lines = list(clean_lines(string.splitlines()))
        params = {}
        for line in lines:
            for sline in line.split(';'):
                m = re.match(r'(\w+)\s*=\s*(.*)', sline.strip())
                if m:
                    key = m.group(1).strip()
                    val = m.group(2).strip()
                    val = Incar.proc_val(key, val)
                    params[key] = val
        return Incar(params)

    @staticmethod
    def proc_val(key, val):
        """
        Static helper method to convert INCAR parameters to proper types, e.g.,
        integers, floats, lists, etc.

        Args:
            key: INCAR parameter key
            val: Actual value of INCAR parameter.
        """
        list_keys = ("LDAUU", "LDAUL", "LDAUJ", "MAGMOM", "DIPOL",
                     "LANGEVIN_GAMMA", "QUAD_EFG", "EINT")
        bool_keys = ("LDAU", "LWAVE", "LSCALU", "LCHARG", "LPLANE", "LUSE_VDW",
                     "LHFCALC", "ADDGRID", "LSORBIT", "LNONCOLLINEAR")
        float_keys = ("EDIFF", "SIGMA", "TIME", "ENCUTFOCK", "HFSCREEN",
                      "POTIM", "EDIFFG", "AGGAC", "PARAM1", "PARAM2")
        int_keys = ("NSW", "NBANDS", "NELMIN", "ISIF", "IBRION", "ISPIN",
                    "ICHARG", "NELM", "ISMEAR", "NPAR", "LDAUPRINT", "LMAXMIX",
                    "ENCUT", "NSIM", "NKRED", "NUPDOWN", "ISPIND", "LDAUTYPE",
                    "IVDW")

        def smart_int_or_float(numstr):
            import pdb; pdb.set_trace()
            if numstr.find(".") != -1 or numstr.lower().find("e") != -1:
                return float(numstr)
            else:
                return int(numstr)
        try:
            if key in list_keys:
                output = []
                toks = re.findall(
                    r"(-?\d+\.?\d*)\*?(-?\d+\.?\d*)?\*?(-?\d+\.?\d*)?", val)
                for tok in toks:
                    if tok[2] and "3" in tok[0]:
                        output.extend(
                            [smart_int_or_float(tok[2])] * int(tok[0])
                            * int(tok[1]))
                    elif tok[1]:
                        output.extend([smart_int_or_float(tok[1])] *
                                      int(tok[0]))
                    else:
                        output.append(smart_int_or_float(tok[0]))
                return output
            if key in bool_keys:
                m = re.match(r"^\.?([T|F|t|f])[A-Za-z]*\.?", val)
                if m:
                    if m.group(1) == "T" or m.group(1) == "t":
                        return True
                    else:
                        return False
                raise ValueError(key + " should be a boolean type!")
            if key in float_keys:
                return float(re.search(r"^-?\d*\.?\d*[e|E]?-?\d*", val).group(0))
            if key in int_keys:
                return int(re.match(r"^-?[0-9]+", val).group(0))
        except ValueError:
            pass
        # Not in standard keys. We will try a hierarchy of conversions.
        try:
            val = int(val)
            return val
        except ValueError:
            pass
        try:
            val = float(val)
            return val
        except ValueError:
            pass
        if "true" in val.lower():
            return True
        if "false" in val.lower():
            return False
        return val.strip().capitalize()

    def diff(self, other):
        similar_param = {}
        different_param = {}
        for k1, v1 in self.items():
            if k1 not in other:
                different_param[k1] = {"INCAR1": v1, "INCAR2": None}
            elif v1 != other[k1]:
                different_param[k1] = {"INCAR1": v1, "INCAR2": other[k1]}
            else:
                similar_param[k1] = v1
        for k2, v2 in other.items():
            if k2 not in similar_param and k2 not in different_param:
                if k2 not in self:
                    different_param[k2] = {"INCAR1": None, "INCAR2": v2}
        return {"Same": similar_param, "Different": different_param}

    def __add__(self, other):
        params = {k: v for k, v in self.items()}
        for k, v in other.items():
            if k in self and v != self[k]:
                raise ValueError("Incars have conflicting values!")
            else:
                params[k] = v
        return Incar(params)



class Potcar(list):
    """
    This class can generate POTCAR file from POSCAR and you can specify
    some functional potcar you want to choose
    """

    def __init__(self,poscar='POSCAR',functional='paw_PBE',sym_potcar_map=None):

        with open(poscar,'r') as f:
            lines = f.readlines()
        atom_type = lines[5].strip()
        if len(atom_type) != 1:
            atom_type = re.split(pattern=r"\s+",string=atom_type)
        else:
            atom_type = list(atom_type)
        self.atom_type = atom_type
        new_sym_potcar_map = []
        if not sym_potcar_map:
            sym_potcar_map = []
        elif isinstance(sym_potcar_map,str):
            sym_potcar_map = list(sym_potcar_map)
        for atom in self.atom_type:
            add_map = False
            for map in sym_potcar_map:
                if atom in map:
                    new_sym_potcar_map.append(map)
                    add_map = True
                    break
            if not add_map:
                new_sym_potcar_map.append(atom)
            self.sym_potcar_map = new_sym_potcar_map
        self.functional = functional

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        res = 'The functional is : ' + self.functional + '\n'
        for i in range(len(self.atom_type)):
            res += 'Atom '+self.atom_type[i]+'using '+self.sym_potcar_map[i]+' type'+'\n'
        return res

    def write_file(self,filename='POTCAR'):
        with open('conf.json') as f:
            json_f = json.load(f)
        potcar_main_dir_path = json_f['potcar_path'][self.functional]
        all_pot_file = []
        for map in self.sym_potcar_map:
            pot_path = path.join(potcar_main_dir_path,map)
            if path.isfile(path.join(pot_path,'POTCAR')):
                all_pot_file.append(path.join(pot_path,'POTCAR'))
            elif path.isfile(path.join(pot_path,'POTCAR.Z')):
                all_pot_file.append(path.join(pot_path,'POTCAR.Z'))
        with open(filename, 'w') as outfile:
            for fname in all_pot_file:
                filename, file_extension = path.splitext(fname)
                if 'Z' in file_extension:
                    with open(fname,'rb') as infile:
                        outfile.write(unlzw(infile.read()).decode('utf-8'))
                else:
                    with open(fname,'r') as infile:
                        for line in nfile.readlines():
                            outfile.write(line)


if __name__ == "__main__":
    potcar = Potcar(functional='USPP_LDA',sym_potcar_map='Zr_pv')
    potcar.write_file()
