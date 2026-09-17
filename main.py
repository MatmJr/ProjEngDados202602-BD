from src.extract import Extract
from src.load import Load
from src.transform import Transform

extrator = Extract()
# pnadc = extrator.extract_pnadc()
# print("Extração efetuada com sucesso!")
pnadc = extrator.extract_collection_from_mongo("IBGE", "PNADC")

transformer = Transform()
df = transformer.transform_pnadc(pnadc)

loader = Load()
# loader.load_json("pernambuco", pnadc)
# print("Dados salvos no formato Json!")
# loader.load_mongo(pnadc, "IBGE", "PNADC")
# print("Dados salvos no Mongo!")
loader.load_sqlite(df)