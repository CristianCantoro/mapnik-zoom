#!/usr/bin/env python

from lxml import etree

ZOOM = [
    559082264,
    279541132,
    139770566,
    69885283,
    34942642,
    17471321,
    8735660,
    4367830,
    2183915,
    1091958,
    545979,
    272989,
    136495,
    68247,
    34124,
    17062,
    8531,
    4265,
    2133,
    1066,
    533
]


class Styles(list):

    def __init__(self):
        super(Styles, self).__init__()

    def __getitem__(self, index):
        if isinstance(index, str) or isinstance(index, unicode):
            return self.find_by_name(index)
        else:
            return super(Styles, self).__getitem__(index)

    def find_by_name(self, name):
        res = [s for s in self if s['name'] == name]
        if not res:
            raise KeyError('No style with name: "{}"'.format(name))
        return res[0]

    def find_by_scale(self, scale_min, scale_max):
        new_styles = Styles()

        for style in self:
            flag = False
            for rule in style['rules']:
                flag_min = False
                flag_max = False
                rmin = int(rule.get('MinScaleDenominator', 0))
                rmax = int(rule.get('MaxScaleDenominator', ZOOM[0]))

                if rmin <= scale_min:
                    flag_min = True

                if rmax >= scale_max:
                    flag_max = True

                if flag_min and flag_max:
                    flag = True

                if flag:
                    new_styles.append(style)
                    break

            if flag:
                continue

        return new_styles

    def with_scale_leq_than(self, scale_max):
        return self.find_by_scale(scale_min=0, scale_max=scale_max)

    def with_scale_geq_than(self, scale_min):
        return self.find_by_scale(scale_min=scale_min, scale_max=ZOOM[0])

    @staticmethod
    def zoom_limits(zoom):
        if zoom < -1 or zoom > 20:
            raise IndexError('Zoom level should be an integer z with'
                             ' 0 <= z <= 20'
                             )
        zmax = ZOOM[zoom]
        if zoom == 20:
            zmin = 0
        else:
            zmin = ZOOM[zoom+1]

        return (zmin, zmax)

    def visible_at_zoom_level(self, zoom):
        zmin, zmax = self.zoom_limits(zoom)

        print zmin, zmax

        return self.find_by_scale(zmin, zmax)


class Layers(list):

    def __init__(self):
        super(Layers, self).__init__()

    def __getitem__(self, index):
        if isinstance(index, str) or isinstance(index, unicode):
            return self.find_by_name(index)
        else:
            return super(Layers, self).__getitem__(index)

    def find_by_name(self, name):
        res = [l for l in self if l['name'] == name]
        if not res:
            raise KeyError('No layer with name: "{}"'.format(name))
        return res[0]

    def with_style(self, style):
        new_layers = Layers()

        for l in self:
            if isinstance(style, str) or isinstance(style, unicode):
                if style in l['styles']:
                    new_layers.append(l)
            elif isinstance(style, list) or isinstance(style, tuple):
                set_styles = set(style)
                if set_styles.intersection(l['styles']):
                    new_layers.append(l)

        return new_layers


if __name__ == '__main__':
    with open('mapnik.xml', 'r') as infile:
        text = infile.read()

    root = etree.fromstring(text)

    styles = Styles()
    for style in root.iterfind('Style'):
        el_style = {}
        el_style.update(style.items())
        el_style['rules'] = []

        for rule in style.iterchildren():
            if rule.tag != 'Rule':
                print 'Not Rule'
                import pdb
                pdb.set_trace()

            el_rule = {}
            ch = None
            for ch in rule.iterchildren():
                if ch.tag in ['MinScaleDenominator', 'MaxScaleDenominator']:
                    el_rule[ch.tag] = ch.text

            el_style['rules'].append(el_rule)

        styles.append(el_style)

    layers = Layers()
    for layer in root.iterfind('Layer'):
        el_layer = {}
        el_layer.update(layer.items())
        el_layer['datasources'] = []
        el_layer['styles'] = []

        for child in layer.iterchildren():
            if child.tag == 'StyleName':
                el_layer['styles'].append(child.text)

            elif child.tag == 'Datasource':
                for parameter in child.iterchildren():
                    el_parameter = {}
                    el_parameter.update(parameter.items())
                    el_parameter['parameter'] = parameter.text
                    el_layer['datasources'].append(el_parameter)

        layers.append(el_layer)

    import pdb
    pdb.set_trace()
