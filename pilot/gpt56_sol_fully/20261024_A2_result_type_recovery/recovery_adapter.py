"""Numeric Result -> official str(parsed value), with exact decimal equivalence checks."""
import json,math
from decimal import Decimal

class NumericLiteral(str):pass

def unique(pairs):
 d={}
 for k,v in pairs:
  if k in d:raise ValueError('DUPLICATE_KEY')
  d[k]=v
 return d

def reject(value):raise ValueError('NONFINITE_JSON_NUMBER')

def convert(text):
 original=json.loads(text,object_pairs_hook=unique,parse_constant=reject)
 literals=json.loads(text,object_pairs_hook=unique,parse_int=NumericLiteral,parse_float=NumericLiteral,parse_constant=reject)
 if not isinstance(original,list):raise ValueError('NOT_ARRAY')
 output=[];audit=[]
 for i,row in enumerate(original):
  if not isinstance(row,dict) or set(row)!={'Task','Dataset','Metric','Result'}:raise ValueError('INVALID_FIELDS')
  if not all(isinstance(row[k],str) for k in ['Task','Dataset','Metric']):raise ValueError('INVALID_NON_RESULT_FIELD')
  value=row['Result'];literal=literals[i]['Result'];result=value;entry={'record_index':i,'original_type':type(value).__name__,'changed_type':False}
  if isinstance(value,str):pass
  elif type(value) in (int,float):
   if type(value) is float and not math.isfinite(value):raise ValueError('NONFINITE_RESULT')
   result=str(value)
   if not isinstance(literal,NumericLiteral) or Decimal(literal)!=Decimal(result):raise ValueError('NUMERIC_PRECISION_LOSS')
   entry.update(original_numeric_literal=str(literal),numeric_semantics_equal=True,changed_type=True)
  else:raise ValueError('UNAPPROVED_RESULT_TYPE')
  entry['compatible_string']=result
  copied={k:(result if k=='Result' else v) for k,v in row.items()}
  assert list(copied)==list(row)
  output.append(copied);audit.append(entry)
 return output,audit
