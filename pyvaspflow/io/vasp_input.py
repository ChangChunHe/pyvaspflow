#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-


from pyvaspflow.utils import str_delimited, clean_lines,zread,read_json
import re,math,json,seekpath
from os import path
import numpy as np
from enum import Enum
from pyvaspflow.utils import is_2d_structure

class Incar(dict):

    def __init__(self, params=None):
        self.update({'ISIF':2,'ISTART':0,'ICHARG':2,'NSW':50,'IBRION':2,
        'EDIFF':1E-5,'EDIFFG':-0.01,'ISMEAR':0,'NPAR':4,'LREAL':'Auto',
        'LWAVE':'F','LCHARG':'F'})
        if params:
            if (params.get("MAGMOM") and isinstance(params["MAGMOM"][0], (int, float))) \
                    and (params.get("LSORBIT") or params.get("LNONCOLLINEAR")):
                val = []
                for i in range(len(params["MAGMOM"])//3):
                    val.append(params["MAGMOM"][i*3:(i+1)*3])
                params["MAGMOM"] = val
            self.update(params)

    def __setitem__(self, key, val):
        key = key.strip()
        val = Incar.proc_val(key.strip(), str(val).strip())
        super().__setitem__(key, val)

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

    def from_file(self,filename):
        with open(filename, "r") as f:
             self.update(Incar.from_string(f.read()))

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
        return params

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
            sym_potcar_map = [sym_potcar_map]
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
        json_f = read_json()
        potcar_main_dir_path = json_f['potcar_path'][self.functional]
        all_pot_file = []
        for map in self.sym_potcar_map:
            pot_path = path.join(potcar_main_dir_path,map)
            if path.isfile(path.join(pot_path,'POTCAR')):
                all_pot_file.append(path.join(pot_path,'POTCAR'))
            elif path.isfile(path.join(pot_path,'POTCAR.Z')):
                all_pot_file.append(path.join(pot_path,'POTCAR.Z'))
            else:
                from os import listdir
                from os.path import isfile, join
                possible = [dir for dir in  listdir(json_f['potcar_path'][self.functional]) if map.split('_')[0] in dir]
                raise FileNotFoundError('Not found supported POTCAR file'
                      +' you can change your map to:'+ ' '.join(possible))
        with open(filename, 'w') as outfile:
            for fname in all_pot_file:
                outfile.write(zread(fname))


class Kpoints_supported_modes(Enum):
    Automatic = 0
    Gamma = 1
    Monkhorst = 2
    Line_mode = 3
    Cartesian = 4
    Reciprocal = 5

    def __str__(self):
        return self.name

    @staticmethod
    def from_string(s):
        c = s.lower()[0]
        for m in Kpoints_supported_modes:
            if m.name.lower()[0] == c:
                return m
        raise ValueError("Can't interprete Kpoint mode %s" % s)


class Kpoints:
    supported_modes = Kpoints_supported_modes

    def __init__(self, comment="Default gamma", num_kpts=0,
                 style=supported_modes.Gamma,
                 kpts=((1, 1, 1),), kpts_shift=(0, 0, 0),
                 kpts_weights=None, coord_type=None, labels=None,
                 tet_number=0, tet_weight=0, tet_connections=None):
        """
        Highly flexible constructor for Kpoints object.  The flexibility comes
        at the cost of usability and in general, it is recommended that you use
        the default constructor only if you know exactly what you are doing and
        requires the flexibility.  For most usage cases, the three automatic
        schemes can be constructed far more easily using the convenience static
        constructors (automatic, gamma_automatic, monkhorst_automatic) and it
        is recommended that you use those.
        Args:
            comment (str): String comment for Kpoints
            num_kpts: Following VASP method of defining the KPOINTS file, this
                parameter is the number of kpoints specified. If set to 0
                (or negative), VASP automatically generates the KPOINTS.
            style: Style for generating KPOINTS.  Use one of the
                Kpoints.supported_modes enum types.
            kpts (2D array): 2D array of kpoints.  Even when only a single
                specification is required, e.g. in the automatic scheme,
                the kpts should still be specified as a 2D array. e.g.,
                [[20]] or [[2,2,2]].
            kpts_shift (3x1 array): Shift for Kpoints.
            kpts_weights: Optional weights for kpoints.  Weights should be
                integers. For explicit kpoints.
            coord_type: In line-mode, this variable specifies whether the
                Kpoints were given in Cartesian or Reciprocal coordinates.
            labels: In line-mode, this should provide a list of labels for
                each kpt. It is optional in explicit kpoint mode as comments for
                k-points.
            tet_number: For explicit kpoints, specifies the number of
                tetrahedrons for the tetrahedron method.
            tet_weight: For explicit kpoints, specifies the weight for each
                tetrahedron for the tetrahedron method.
            tet_connections: For explicit kpoints, specifies the connections
                of the tetrahedrons for the tetrahedron method.
                Format is a list of tuples, [ (sym_weight, [tet_vertices]),
                ...]
        The default behavior of the constructor is for a Gamma centered,
        1x1x1 KPOINTS with no shift.
        """
        if num_kpts > 0 and (not labels) and (not kpts_weights):
            raise ValueError("For explicit or line-mode kpoints, either the "
                             "labels or kpts_weights must be specified.")
        self.comment = comment
        self.num_kpts = num_kpts
        self.kpts = kpts
        self.style = style
        self.coord_type = coord_type
        self.kpts_weights = kpts_weights
        self.kpts_shift = kpts_shift
        self.labels = labels
        self.tet_number = tet_number
        self.tet_weight = tet_weight
        self.tet_connections = tet_connections

    @property
    def style(self):
        return self._style

    @style.setter
    def style(self, style):
        if isinstance(style, str):
            style = Kpoints.supported_modes.from_string(style)

        if style in (Kpoints.supported_modes.Automatic,
                     Kpoints.supported_modes.Gamma,
                     Kpoints.supported_modes.Monkhorst) and len(self.kpts) > 1:
            raise ValueError("For fully automatic or automatic gamma or monk "
                             "kpoints, only a single line for the number of "
                             "divisions is allowed.")
        self._style = style

    def automatic(self,subdivisions):
        """
        Convenient static constructor for a fully automatic Kpoint grid, with
        gamma centered Monkhorst-Pack grids and the number of subdivisions
        along each reciprocal lattice vector determined by the scheme in the
        VASP manual.
        Args:
            subdivisions: Parameter determining number of subdivisions along
                each reciprocal lattice vector.
        """
        self.comment = "Fully automatic kpoint scheme"
        self.num_kpts = 0
        self._style=Kpoints.supported_modes.Automatic
        self.kpts=[[subdivisions]]


    def gamma_automatic(self, kpts=(1, 1, 1), shift=(0, 0, 0)):
        """
        Convenient static constructor for an automatic Gamma centered Kpoint
        grid.
        Args:
            kpts: Subdivisions N_1, N_2 and N_3 along reciprocal lattice
                vectors. Defaults to (1,1,1)
            shift: Shift to be applied to the kpoints. Defaults to (0,0,0).
        """

        self.comment = "Fully automatic kpoint scheme"
        self.num_kpts = 0
        self._style = Kpoints.supported_modes.Gamma
        self.kpts = [kpts]
        self.kpts_shift = shift

    def monkhorst_automatic(self, kpts=(2, 2, 2), shift=(0, 0, 0)):
        """
        Convenient static constructor for an automatic Monkhorst pack Kpoint
        grid.
        Args:
            kpts: Subdivisions N_1, N_2 and N_3 along reciprocal lattice
                vectors. Defaults to (2,2,2)
            shift: Shift to be applied to the kpoints. Defaults to (0,0,0).
        """
        self.comment = "Automatic kpoint scheme"
        self.num_kpts =  0
        self._style = Kpoints.supported_modes.Monkhorst
        self.kpts = [kpts]
        self.kpts_shift = shift


    def automatic_density(self, structure, kppa, force_gamma=False):
        """
        Returns an automatic Kpoint object based on a structure and a kpoint
        density. Uses Gamma centered meshes for hexagonal cells and
        Monkhorst-Pack grids otherwise.
        Algorithm:
            Uses a simple approach scaling the number of divisions along each
            reciprocal lattice vector proportional to its length.
        Args:
            structure (Structure): Input structure
            kppa (int): Grid density
            force_gamma (bool): Force a gamma centered mesh (default is to
                use gamma only for hexagonal cells or odd meshes)
        """
        comment = "grid density = %.0f / atom"%kppa
        if math.fabs((math.floor(kppa ** (1 / 3) + 0.5)) ** 3 - kppa) < 1:
            kppa += kppa * 0.01
        ngrid = kppa / len(structure.atoms)
        latt = structure.lattice
        lengths = np.linalg.norm(latt,axis=1)
        is_2d = is_2d_structure(structure)

        if type(is_2d) is tuple:
            print('This structure will be treated as a two dimensional structure here',
            'so the mesh of  one direction will be set to 1')
            vac_idx = is_2d[1]
            atom_idx = np.setdiff1d(range(3),vac_idx)
            mult = (ngrid * lengths[atom_idx[0]] * lengths[atom_idx[1]]) ** (1 / 2)
            num_div = np.zeros((3,))
            num_div[atom_idx[0]] = int(math.floor(max(mult / lengths[atom_idx[0]], 1)))
            num_div[atom_idx[1]] = int(math.floor(max(mult / lengths[atom_idx[1]], 1)))
            num_div[vac_idx] = 1
            num_div = num_div.astype(int).tolist()
        elif not is_2d :
            mult = (ngrid * lengths[0] * lengths[1] * lengths[2]) ** (1 / 3)
            num_div = [int(math.floor(max(mult / l, 1))) for l in lengths]

        spg = structure.get_spacegroup()
        if int(spg.split('(')[1].split(')')[0]) in range(168,195):
            is_hexagonal = True#   latt.is_hexagonal()
        else:
            is_hexagonal = False
        has_odd = any([i % 2 == 1 for i in num_div])
        if has_odd or is_hexagonal or force_gamma:
            style = Kpoints.supported_modes.Gamma
        else:
            style = Kpoints.supported_modes.Monkhorst
        self.comment = comment
        self.num_kpts =  0
        self._style = style
        self.kpts = [num_div]
        self.kpts_shift = [0,0,0]

    def automatic_gamma_density(self,structure, kppa):
        """
        Returns an automatic Kpoint object based on a structure and a kpoint
        density. Uses Gamma centered meshes always. For GW.
        """
        latt = structure.lattice
        ngrid = kppa / len(structure.atoms)
        lengths = np.linalg.norm(latt,axis=1)
        is_2d = is_2d_structure(structure)
        if type(is_2d) is tuple:
            print('This structure will be treated as a two dimensional structure here',
            'so the mesh of  one direction will be set to 1 or 2')
            vac_idx = is_2d[1]
            atom_idx = np.setdiff1d(range(3),vac_idx)
            mult = (ngrid * lengths[atom_idx[0]] * lengths[atom_idx[1]]) ** (1 / 2)
            num_div = np.zeros((3,))
            num_div[atom_idx[0]] = int(math.floor(max(mult / lengths[atom_idx[0]], 1)))
            num_div[atom_idx[1]] = int(math.floor(max(mult / lengths[atom_idx[1]], 1)))
            num_div[vac_idx] = 1
            num_div = num_div.astype(int).tolist()
        elif not is_2d :
            mult = (ngrid * lengths[0] * lengths[1] * lengths[2]) ** (1 / 3)
            num_div = [int(math.floor(max(mult / l, 1))) for l in lengths]
        # ensure that numDiv[i] > 0
        num_div = [i if i > 0 else 1 for i in num_div]
        # VASP documentation recommends to use even grids for n <= 8 and odd
        # grids for n > 8.
        # num_div = [i + i % 2 if i <= 8 else i - i % 2 + 1 for i in num_div]
        style = Kpoints.supported_modes.Gamma
        comment = "KPOINTS with grid density = " +"{} / atom".format(kppa)
        self.comment = comment
        self.num_kpts =  0
        self._style = style
        self.kpts = [num_div]
        self.kpts_shift = [0,0,0]


    def automatic_density_by_vol(self,structure, kppvol, force_gamma=False):
        """
        Returns an automatic Kpoint object based on a structure and a kpoint
        density per inverse Angstrom^3 of reciprocal cell.
        Algorithm:
            Same as automatic_density()
        Args:
            structure (Structure): Input structure
            kppvol (int): Grid density per Angstrom^(-3) of reciprocal cell
            force_gamma (bool): Force a gamma centered mesh
        """
        # vol = structure.lattice.reciprocal_lattice.volume
        latt = structure.lattice
        latt_vol = np.linalg.det(latt)
        r_x = np.cross(latt[1],latt[2])/latt_vol
        r_y = np.cross(latt[2],latt[0])/latt_vol
        r_z = np.cross(latt[0],latt[1])/latt_vol
        vol = 2*np.pi*np.linalg.det([r_x,r_y,r_z])
        kppa = kppvol * vol * len(structure.atoms)
        self.comment = "KPOINTS with grid density = " +"{} / atom".format(kppa)
        self.num_kpts =  0
        if force_gamma:
            self._style = Kpoints.supported_modes.Gamma
        else:
            self._style = Kpoints.supported_modes.Monkhorst
        lengths = np.linalg.norm(latt,axis=1)
        ngrid = kppa / len(structure.atoms)
        mult = (ngrid * lengths[0] * lengths[1] * lengths[2]) ** (1 / 3)
        num_div = [int(math.floor(max(mult / l, 1))) for l in lengths]
        spg = structure.get_spacegroup()
        if int(spg.split('(')[1].split(')')[0]) in range(168,195):
            is_hexagonal = True#   latt.is_hexagonal()
        else:
            is_hexagonal = False
        has_odd = any([i % 2 == 1 for i in num_div])
        self.kpts = [num_div]
        self.kpts_shift = [0,0,0]


    def automatic_linemode(self, structure,num_kpts=16):
        all_kpath = seekpath.get_explicit_k_path((structure.lattice,
        structure.positions,structure.atoms))
        points = all_kpath['point_coords']
        path = all_kpath['path']
        kpoints,labels = [],[]
        for p in path:
            kpoints.append(points[p[0]])
            kpoints.append(points[p[1]])
            labels.append(p[0])
            labels.append(p[1])

        comment = 'Line_mode KPOINTS file, '+'num_kpts: '+str(num_kpts)
        self.comment = comment
        self._style = Kpoints.supported_modes.Line_mode
        self.coord_type = 'Reciprocal'
        self.kpts = kpoints
        self.labels = labels
        self.num_kpts = num_kpts

    @staticmethod
    def from_file(filename):
        """
        Reads a Kpoints object from a KPOINTS file.
        Args:
            filename (str): filename to read from.
        Returns:
            Kpoints object
        """
        with open(filename, "rt") as f:
            return Kpoints.from_string(f.read())

    @staticmethod
    def from_string(string):
        """
        Reads a Kpoints object from a KPOINTS string.
        Args:
            string (str): KPOINTS string.
        Returns:
            Kpoints object
        """
        lines = [line.strip() for line in string.splitlines()]

        comment = lines[0]
        num_kpts = int(lines[1].split()[0].strip())
        style = lines[2].lower()[0]

        # Fully automatic KPOINTS
        if style == "a":
            return Kpoints.automatic(int(lines[3]))

        coord_pattern = re.compile(r'^\s*([\d+.\-Ee]+)\s+([\d+.\-Ee]+)\s+'
                                   r'([\d+.\-Ee]+)')

        # Automatic gamma and Monk KPOINTS, with optional shift
        if style == "g" or style == "m":
            kpts = [int(i) for i in lines[3].split()]
            kpts_shift = (0, 0, 0)
            if len(lines) > 4 and coord_pattern.match(lines[4]):
                try:
                    kpts_shift = [float(i) for i in lines[4].split()]
                except ValueError:
                    pass
            return Kpoints.gamma_automatic(kpts, kpts_shift) if style == "g" \
                else Kpoints.monkhorst_automatic(kpts, kpts_shift)

        # Automatic kpoints with basis
        if num_kpts <= 0:
            style = Kpoints.supported_modes.Cartesian if style in "ck" \
                else Kpoints.supported_modes.Reciprocal
            kpts = [[float(j) for j in lines[i].split()] for i in range(3, 6)]
            kpts_shift = [float(i) for i in lines[6].split()]
            return Kpoints(comment=comment, num_kpts=num_kpts, style=style,
                           kpts=kpts, kpts_shift=kpts_shift)

        # Line-mode KPOINTS, usually used with band structures
        if style == "l":
            coord_type = "Cartesian" if lines[3].lower()[0] in "ck" \
                else "Reciprocal"
            style = Kpoints.supported_modes.Line_mode
            kpts = []
            labels = []
            patt = re.compile(r'([e0-9.\-]+)\s+([e0-9.\-]+)\s+([e0-9.\-]+)'
                              r'\s*!*\s*(.*)')
            for i in range(4, len(lines)):
                line = lines[i]
                m = patt.match(line)
                if m:
                    kpts.append([float(m.group(1)), float(m.group(2)),
                                 float(m.group(3))])
                    labels.append(m.group(4).strip())
            return Kpoints(comment=comment, num_kpts=num_kpts, style=style,
                           kpts=kpts, coord_type=coord_type, labels=labels)

        # Assume explicit KPOINTS if all else fails.
        style = Kpoints.supported_modes.Cartesian if style in "ck" \
            else Kpoints.supported_modes.Reciprocal
        kpts = []
        kpts_weights = []
        labels = []
        tet_number = 0
        tet_weight = 0
        tet_connections = None

        for i in range(3, 3 + num_kpts):
            toks = lines[i].split()
            kpts.append([float(j) for j in toks[0:3]])
            kpts_weights.append(float(toks[3]))
            if len(toks) > 4:
                labels.append(toks[4])
            else:
                labels.append(None)
        try:
            # Deal with tetrahedron method
            if lines[3 + num_kpts].strip().lower()[0] == "t":
                toks = lines[4 + num_kpts].split()
                tet_number = int(toks[0])
                tet_weight = float(toks[1])
                tet_connections = []
                for i in range(5 + num_kpts, 5 + num_kpts + tet_number):
                    toks = lines[i].split()
                    tet_connections.append((int(toks[0]),
                                            [int(toks[j])
                                             for j in range(1, 5)]))
        except IndexError:
            pass

        return Kpoints(comment=comment, num_kpts=num_kpts,
                       style=Kpoints.supported_modes[str(style)],
                       kpts=kpts, kpts_weights=kpts_weights,
                       tet_number=tet_number, tet_weight=tet_weight,
                       tet_connections=tet_connections, labels=labels)

    def write_file(self, filename='KPOINTS'):
        with open(filename, "wt") as f:
            f.write(self.__str__())

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        lines = [self.comment, str(self.num_kpts), self.style.name]
        style = self.style.name.lower()[0]
        if style == "l":
            lines.append(self.coord_type)
        for i in range(len(self.kpts)):
            lines.append(" ".join([str(x) for x in self.kpts[i]]))
            if style == "l":
                lines[-1] += " ! " + self.labels[i]
                if i % 2 == 1:
                    lines[-1] += "\n"
            elif self.num_kpts > 0:
                if self.labels is not None:
                    lines[-1] += " %i %s" % (self.kpts_weights[i],
                                             self.labels[i])
                else:
                    lines[-1] += " %i" % (self.kpts_weights[i])

        # Print tetrahedron parameters if the number of tetrahedrons > 0
        if style not in "lagm" and self.tet_number > 0:
            lines.append("Tetrahedron")
            lines.append("%d %f" % (self.tet_number, self.tet_weight))
            for sym_weight, vertices in self.tet_connections:
                lines.append("%d %d %d %d %d" % (sym_weight, vertices[0],
                                                 vertices[1], vertices[2],
                                                 vertices[3]))

        # Print shifts for automatic kpoints types if not zero.
        if self.num_kpts <= 0 and tuple(self.kpts_shift) != (0, 0, 0):
            lines.append(" ".join([str(x) for x in self.kpts_shift]))
        return "\n".join(lines) + "\n"

    def as_dict(self):
        """json friendly dict representation of Kpoints"""
        d = {"comment": self.comment, "nkpoints": self.num_kpts,
             "generation_style": self.style.name, "kpoints": self.kpts,
             "usershift": self.kpts_shift,
             "kpts_weights": self.kpts_weights, "coord_type": self.coord_type,
             "labels": self.labels, "tet_number": self.tet_number,
             "tet_weight": self.tet_weight,
             "tet_connections": self.tet_connections}

        optional_paras = ["genvec1", "genvec2", "genvec3", "shift"]
        for para in optional_paras:
            if para in self.__dict__:
                d[para] = self.__dict__[para]
        d["@module"] = self.__class__.__module__
        d["@class"] = self.__class__.__name__
        return d

    @classmethod
    def from_dict(cls, d):
        comment = d.get("comment", "")
        generation_style = d.get("generation_style")
        kpts = d.get("kpoints", [[1, 1, 1]])
        kpts_shift = d.get("usershift", [0, 0, 0])
        num_kpts = d.get("nkpoints", 0)
        return cls(comment=comment, kpts=kpts, style=generation_style,
                   kpts_shift=kpts_shift, num_kpts=num_kpts,
                   kpts_weights=d.get("kpts_weights"),
                   coord_type=d.get("coord_type"),
                   labels=d.get("labels"), tet_number=d.get("tet_number", 0),
                   tet_weight=d.get("tet_weight", 0),
                   tet_connections=d.get("tet_connections"))


if __name__ == '__main__':
    from sagar.io.vasp import read_vasp
    c = read_vasp('/home/hecc/Documents/python-package/Defect-Formation-Calculation/pyvaspflow/examples/POSCAR')
    kpoints = Kpoints()
    kpoints.automatic_density(structure=c,kppa=3000)
    kpoints.write_file()
