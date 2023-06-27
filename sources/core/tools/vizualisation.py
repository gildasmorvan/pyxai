import matplotlib.pyplot as pyplot
import matplotlib as mpl
from matplotlib.ticker import MaxNLocator
import numpy
from PIL import Image as PILImage
from PIL.ImageQt import ImageQt


class Image:

    def __init__(self, size, title):
        self.size = size
        self.features = []
        self.images = []
        self.title = title
        self.background = None


    def set_instance(self, instance):
        self.images.append(numpy.zeros(self.size))
        self.images[-1] = numpy.reshape(instance, self.size)
        return self


    def set_background_instance(self, background):
        self.background = numpy.zeros(self.size)
        self.background = numpy.reshape(background, self.size)
        return self


    def add_reason(self, reason):
        self.images.append([numpy.zeros(self.size), numpy.zeros(self.size)])
        images = self.images[-1]
        with_weights = all(feature["weight"] is not None for feature in reason)
        if with_weights:
            max_weights = max(feature["weight"] for feature in reason if feature["weight"])
            min_weights = min(feature["weight"] for feature in reason if feature["weight"])

        for feature in reason:
            id_feature = feature["id"]
            sign = feature["sign"]
            weight = feature["weight"]

            x = (id_feature - 1) // self.size[0]
            y = (id_feature - 1) % self.size[1]
            color = (weight / (max_weights - min_weights)) * 256 if with_weights else 256
            if sign:
                images[0][x][y] = color
            else:
                images[1][x][y] = color

        images[0] = numpy.ma.masked_where(images[0] < 0.9, images[0])
        images[1] = numpy.ma.masked_where(images[1] < 0.9, images[1])
        return self

class PyPlotDiagramGenerator():
    def __init__(self):
        pass

    def convert_features_to_dict_features(self, features):
        dict_features = dict()
        for feature in features:
            name = feature["name"]
            if name not in dict_features.keys():
                dict_features[name] = [feature]
            else:
                dict_features[name].append(feature)
        return dict_features
    
    def generate_explanation(self, feature_values, instance, reason):

        color_blue = "#4169E1"
        color_red = "#CD5C5C"
        color_grey = "#808080"
        trans_left = mpl.transforms.Affine2D().translate(-5, 0)
        trans_right = mpl.transforms.Affine2D().translate(5, 0)
        
        mpl.rcParams['axes.spines.left'] = False
        mpl.rcParams['axes.spines.right'] = False
        mpl.rcParams['axes.spines.top'] = False
        mpl.rcParams['axes.spines.bottom'] = True
        dict_features = reason
        fig, axes = pyplot.subplots(len(dict_features.keys()), figsize=(6,len(dict_features.keys())+3))
        for i, feature in enumerate(dict_features.keys()):
            if "string" not in dict_features[feature][0].keys():
                
                raise ValueError("The string version of this feature is not done.")
            string_view = dict_features[feature][0]["string"]
            theory = dict_features[feature][0]["theory"] 
            
            bound_left = 0
            bound_right = 1
            bound_explanation_left = None
            bound_explanation_right = None
            
            if theory is not None:
                if theory[0] == "binary":
                    #binary case
                    feature_str, operator_str, threshold_str = string_view.split(" ")
                    
                    if operator_str == "=":
                        colors = [color_blue, color_red] if threshold_str == "0" else [color_red, color_blue]
                    else:
                        colors = [color_red, color_blue] if threshold_str == "0" else [color_blue, color_red]
                    
                    the_table = axes[i].table(
                        cellText=[["0","1"]],
                        cellColours=[colors],
                        loc='center',
                        colLoc='center',
                        cellLoc='center',
                        bbox=[0, -0.3, 1, 0.275])
                    
                    the_table.set_fontsize(10)
                    axes[i].text(0.5,0.2,feature_str)
                    
                    axes[i].yaxis.set_visible(False)
                    axes[i].xaxis.set_visible(False)
                    axes[i].axis('off')
                    continue
                elif theory[0] == "categorical":
                    #categorical case
                    feature_str, operator_str, values = string_view.split(" ")
                    all_values = [str(element) for element in theory[1][2]]
                    colors = [color_grey] * len(all_values)
                    if operator_str == "=":
                        index = all_values.index(values)
                        for c in range(len(colors)): colors[c] = color_red
                        colors[index] = color_blue
                    elif operator_str == "!=":
                        if "{" in values:
                            values_to_red = [element for element in values.replace("{","").replace("}","").split(",")]
                            for value in values_to_red:
                                index = all_values.index(value)
                                colors[index] = color_red
                        else:
                            index = all_values.index(values)
                            colors[index] = color_red

                    the_table = axes[i].table(
                        cellText=[all_values],
                        cellColours=[colors],
                        loc='center',
                        colLoc='center',
                        cellLoc='center',
                        bbox=[0, -0.3, 1, 0.275])
                    the_table.set_fontsize(10)
                    axes[i].text(0.5,0.2,feature_str)
                    
                    axes[i].yaxis.set_visible(False)
                    axes[i].xaxis.set_visible(False)
                    axes[i].axis('off')
                    
                    continue

            value_instance = feature_values[feature]
            #numerical case: if theory is None, all features are considered as numerical
            if "in" in string_view:
                if "and" in string_view:
                    #case feature in [infinty, threshold1] and feature in [threshold2, infinity]
                    raise NotImplementedError("TODO feature in [infinty, threshold1] and feature in [threshold2, infinity]")
                else:
                    #case feature in [threshold1, threshold2]
                    feature_str, _, threshold_str_1, threshold_str_2 = string_view.split(" ")

                    threshold_1 = threshold_str_1
                    threshold_2 = threshold_str_2
                    
                    threshold_1 = float(threshold_1.replace("[", "").replace("]", "").replace(",", ""))
                    threshold_2 = float(threshold_2.replace("[", "").replace("]", "").replace(",", ""))
                    bound_left = min(threshold_1, threshold_2, value_instance)
                    bound_right = max(threshold_1, threshold_2, value_instance)
                    total = bound_right - bound_left
                    bound_left = bound_left - (total/10)
                    bound_right = bound_right + (total/10)

                    midle = (bound_left+bound_right)/2
                    axes[i].set_ylim(bottom=-1, top=50)
                    axes[i].set_xlim(left=bound_left, right=bound_right)
                    axes[i].plot([bound_left, bound_right], [25, 25], color=color_blue)
                    axes[i].text(midle,35,feature)
                    axes[i].yaxis.set_visible(False)
                    
                    bracket_left = None
                    bound_explanation_left = min(threshold_1, threshold_2)
                    if bound_explanation_left == threshold_1:
                        bracket_left = "$\mathcal{[}$" if "[" in threshold_str_1 else "$\mathcal{]}$"
                    else:
                        bracket_left = "$\mathcal{[}$" if "[" in threshold_str_2 else "$\mathcal{]}$"

                    bracket_right = None
                    bound_explanation_right = max(threshold_1, threshold_2)
                    if bound_explanation_right == threshold_1:
                        bracket_right = "$\mathcal{[}$" if "[" in threshold_str_1 else "$\mathcal{]}$"
                    else:
                        bracket_right = "$\mathcal{[}$" if "[" in threshold_str_2 else "$\mathcal{]}$"

                    axes[i].plot([bound_explanation_left, bound_explanation_right], [25, 25], color=color_blue, linewidth=5)

                    axes[i].plot(value_instance, 25, marker="o", color=color_red, clip_on=False, markersize=10)
                    
                    if bracket_left is not None:
                        x = axes[i].plot(bound_explanation_left, 25, marker=bracket_left, color=color_blue, clip_on=False, markersize=20)
                        if bracket_left == "$\mathcal{]}$": x[0].set_transform(x[0].get_transform()+trans_left)
                    if bracket_right is not None:
                        axes[i].plot(bound_explanation_right, 25, marker=bracket_right, color=color_blue, clip_on=False, markersize=20)
                        if bracket_right == "$\mathcal{[}$": x[0].set_transform(x[0].get_transform()+trans_right)
                    
            else:
                #Case with a simple condition feature > threshold
                feature_str, operator_str, threshold_str = string_view.split(" ")
                threshold = float(threshold_str)
                bound_left = min(threshold, value_instance)
                bound_right = max(threshold, value_instance)
                total = bound_right - bound_left
                if bound_right == bound_left:
                    total = bound_right
                bound_left = bound_left - (total/10)
                bound_right = bound_right + (total/10)
                
                
                midle = (bound_left+bound_right)/2
                axes[i].set_ylim(bottom=-1, top=50)
                axes[i].set_xlim(left=bound_left, right=bound_right)
                axes[i].plot([bound_left, bound_right], [25, 25], color=color_blue)
                axes[i].text(midle,35,feature)
                axes[i].yaxis.set_visible(False)
                
                bracket_left = None
                bracket_right = None
                if operator_str == ">" or operator_str == ">=":
                    bound_explanation_left = threshold
                    bound_explanation_right = bound_right
                    bracket_left = "$\mathcal{[}$" if operator_str == ">=" else "$\mathcal{]}$"
                
                elif operator_str == "<" or operator_str == "<=":
                    bound_explanation_left = bound_left
                    bound_explanation_right = threshold
                    bracket_right = "$\mathcal{[}$" if operator_str == "<" else "$\mathcal{]}$"
                else:
                    raise NotImplementedError("TODO = and !=")
                print("bound_explanation_left:", bound_explanation_left)
                print("bound_explanation_right:", bound_explanation_right)
                
                axes[i].plot([bound_explanation_left, bound_explanation_right], [25, 25], color=color_blue, linewidth=5)
                axes[i].plot(value_instance, 25, marker="o", color=color_red, clip_on=False, markersize=10)
                
                if bracket_left is not None:
                    x = axes[i].plot(threshold, 25, marker=bracket_left, color=color_blue, clip_on=False, markersize=20)
                    if bracket_left == "$\mathcal{]}$": x[0].set_transform(x[0].get_transform()+trans_left)
                
                if bracket_right is not None:
                    x = axes[i].plot(threshold, 25, marker=bracket_right, color=color_blue, clip_on=False, markersize=20)
                    if bracket_right == "$\mathcal{[}$": x[0].set_transform(x[0].get_transform()+trans_right)
                        
                        


                #axes[i].tick_params(top='off', bottom='off', left='off', right='off', labelleft='off', labelbottom='on')
                #invisible = axes[i].plot([0, 100], [2, 2], marker = 'o')
        pyplot.subplots_adjust(top=1, hspace=1)

        #pyplot.figure(figsize=(3.6,0.75*)))
        #pyplot.axis('off')
        pyplot.savefig('tmp_diagram.png', bbox_inches='tight')
        image = PILImage.open('tmp_diagram.png')

        #ess = axes.imshow()
        #print("ess:", ess)
        #new_image = axes.make_image(pyplot.gcf().canvas.get_renderer(), unsampled=True)
        #new_image = PILImage.fromarray(axes[0])
        pyplot.close()
        return ImageQt(image)

class PyPlotImageGenerator():

    def __init__(self, size, n_colors):
        self.size = size
        self.n_colors = n_colors
        
    

    def generate_instance(self, instance):
        image = numpy.zeros(self.size)
        image = numpy.reshape(instance, self.size)
        self.PIL_instance = PILImage.fromarray(numpy.uint8(image))
        return ImageQt(self.PIL_instance)
    
    def generate_explanation(self, instance, reason):
        reason = [reason[key][0] for key in reason.keys()]
        self.image_positive = numpy.zeros(self.size)
        self.image_negative = numpy.zeros(self.size)
        with_weights = all(feature["weight"] is not None for feature in reason)
        if with_weights:
            max_weights = max(feature["weight"] for feature in reason if feature["weight"])
            min_weights = min(feature["weight"] for feature in reason if feature["weight"])

        for feature in reason:
            id_feature = feature["id"]
            sign = feature["sign"]
            weight = feature["weight"]

            x = (id_feature - 1) // self.size[0]
            y = (id_feature - 1) % self.size[1]
            color = (weight / (max_weights - min_weights)) * self.n_colors if with_weights else self.n_colors-1
            if sign:
                self.image_negative[x][y] = color
            else:
                self.image_positive[x][y] = color

        #self.image_negative = numpy.ma.masked_where(self.image_negative < 0.9, self.image_negative)
        #self.image_positive = numpy.ma.masked_where(self.image_positive < 0.9, self.image_positive)
        
        x_1 = pyplot.imshow(PILImage.fromarray(numpy.uint8(self.image_negative)), alpha=0.6, cmap='Blues', vmin=0, vmax=self.n_colors-1, interpolation='None')
        x_2 = pyplot.imshow(PILImage.fromarray(numpy.uint8(self.image_positive)), alpha=0.6, cmap='Reds', vmin=0, vmax=self.n_colors-1, interpolation='None')

        new_image_negative = x_1.make_image(pyplot.gcf().canvas.get_renderer(), unsampled=True)
        new_image_positive = x_2.make_image(pyplot.gcf().canvas.get_renderer(), unsampled=True)
        new_image_negative = PILImage.fromarray(new_image_negative[0])
        new_image_positive = PILImage.fromarray(new_image_positive[0])
            
        fusion = PILImage.blend(new_image_negative, new_image_positive, 0.5)
        if instance is not None:
            image = numpy.zeros(self.size)
            image = numpy.reshape(instance, self.size)
            x_3 = pyplot.imshow(numpy.uint8(image), alpha=0.5, cmap='Greys', vmin=0, vmax=255)
            new_image_x_3 = x_3.make_image(pyplot.gcf().canvas.get_renderer(), unsampled=True)
            new_image_x_3 = PILImage.fromarray(new_image_x_3[0])
            
            fusion = PILImage.blend(fusion, new_image_x_3, 0.2)
        return ImageQt(fusion)
    
class Vizualisation():

    def __init__(self, x, y, instance=None):
        self.size = (x, y)
        self._heat_map_images = []


    '''
    Do not forget to convert an implicant in features thanks to tree.to_features(details=True).
    Create two images per reason, the positive one and the negative one.
    '''


    def new_image(self, title):
        self._heat_map_images.append(Image(self.size, title))
        return self._heat_map_images[-1]


    def display(self, *, n_rows=1):
        n_images = len(self._heat_map_images)
        if n_rows >= n_images:
            n_rows = 1
        fig, axes = pyplot.subplots(n_rows,
                                    n_images if n_rows == 1 else n_images // n_rows + (1 if n_images % n_rows != 0 else 0),
                                    figsize=self.size)
        for i, heat_map_images in enumerate(self._heat_map_images):
            if n_images == 1:
                axes.title.set_text(heat_map_images.title)
            else:
                axes.flat[i].title.set_text(heat_map_images.title)
            for image in heat_map_images.images:
                if isinstance(image, list):
                    if n_images == 1:
                        axes.imshow(image[0], alpha=0.6, cmap='Blues', vmin=0, vmax=255, interpolation='None')
                        axes.imshow(image[0], alpha=0.6, cmap='Reds', vmin=0, vmax=255, interpolation='None')
                    else:
                        a = axes if n_rows == 1 else axes[i // n_rows]
                        idx = i if n_rows == 1 else i % n_rows
                        a.flat[idx].imshow(image[0], alpha=0.6, cmap='Blues', vmin=0, vmax=255, interpolation='None')
                        a.flat[idx].imshow(image[1], alpha=0.6, cmap='Reds', vmin=0, vmax=255, interpolation='None')
                        if heat_map_images.background is not None:
                            a.flat[idx].imshow(heat_map_images.background, alpha=0.2, cmap='Greys', vmin=0, vmax=255)
                else:
                    if n_images == 1:
                        axes.imshow(image)
                    else:
                        axes.flat[i].imshow(image)
        pyplot.show()


    #def display_observation(self):
        #        pyplot.imshow(self.image_observation)
    #    pyplot.show()
