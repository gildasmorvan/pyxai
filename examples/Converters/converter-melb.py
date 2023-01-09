# usage
# python3 examples/Converters/converter-melb.py -dataset=../../melb_data.csv

from pyxai import Learning, Explainer, Tools

import datetime

# Machine learning part
# NUMERICAL: with an order (Ordinal Encoding) 
# CATEGORICAL: without an order 

converter = Learning.Converter(Tools.Options.dataset, target_feature="Type", classification_type=Learning.BINARY_CLASS, to_binary_classification=Learning.ONE_VS_REST) # class Converter

converter.unset_features(["Address", "Suburb", "SellerG"])

converter.set_categorical_features(columns=["Method", "CouncilArea", "Regionname"])

#datetime.date(d.split("/")[2], d.split("/")[1], d.split("/")[0]).toordinal()
converter.set_numerical_features({
  "Postcode": lambda d: int(d),
  "Rooms": None, 
  "Price": None,
  "Date": lambda d: datetime.date(int(d.split("/")[2]), int(d.split("/")[1]), int(d.split("/")[0])).toordinal(), 
  "Distance": None,
  "Bedroom2": None,
  "Bathroom": None,
  "Car": None,
  "Landsize": None,
  "BuildingArea": None,
  "YearBuilt": None,
  "Lattitude": None,
  "Longtitude": None,
  "Propertycount": None
  })

#print(converter.get_types())
converter.process()
dataset_name = Tools.Options.dataset.split("/")[-1].split(".")[0] 
converter.export(dataset_name, output="examples/datasets_converted")

