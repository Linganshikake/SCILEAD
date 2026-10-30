# DeepSeek Fully 逐条核查

## D18-1523.pdf：上下文已含数值但抽取遗漏

第5页表格证据包含FNMI 11.26、FBC 57.49和AVG 25.43；原始预测只保留AVG 25.43 ± 0.48，缺少另外两个指标。

证据：`inputs/D18-1523.pdf/source_documents.json`；原始与标准化记录见 `inspection/examples.json`。

## 1811.09242.pdf：指标与结果绑定错误

原始预测将V-M绑定25.20、AVG绑定10.1；Gold对应V-M=10.1、AVG=25.2。标准化仅替换名称，保留了这两处错绑。FNMI预测9.74，Gold为9.55。

证据：`inputs/1811.09242.pdf/source_documents.json`；原始与标准化记录见 `inspection/examples.json`。

## C18-1139.pdf：逐字段标准化丢失跨字段限定

原始第二条Task=NER German、Dataset=CoNLL-2003、Result=88.32±0.20；标准化分别处理Task与Dataset，将Dataset映射为CoNLL-2003 - English。语言限定在Task中，未进入独立Dataset请求。

证据：`inputs/C18-1139.pdf/source_documents.json`；原始与标准化记录见 `inspection/examples.json`。

原始预测、标准化结果和Gold均未改写。上述为具体实例；总体指标仍按完整43篇计算。
