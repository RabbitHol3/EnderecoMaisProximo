import googlemaps
import dotenv
import sys
import os
from dataclasses import dataclass
import pandas as pd
KEY = os.getenv('GOOGLE_API_KEY')
import time
class BuscadorUBS:
    class Modos:
        DIRIGINDO = "driving"
        ANDANDO = "walking"
        PEDALANDO = "bicycling"
        TRANSITO = "transit"

    lang = "pt-BR"
    ubs_ends: tuple[dict] = ()

    def __init__(self):
        self.maps =  googlemaps.Client(KEY)
    
    def load_ubs(self, path_xlsx:str, sheet:str) -> list[dict]:        
        df =  pd.read_excel(path_xlsx, sheet_name=sheet)
        data = df.to_dict(orient='records')
        # Remove duplicados
        self.ubs_ends += tuple(filter(lambda x: x not in self.ubs_ends, data))
        return self.ubs_ends
    
    def proximo_de(self, endereco:str, modo:'BuscadorUBS.Modos'=Modos.DIRIGINDO)->dict:
        """Coleta o endereco da UBS mais proxima

        Args:
        ------
            `endereco (str)`: Endereco da origem
            ``modo (Modos)``: Especifica o modo de transporte para realizacao do calculo
                `opcional(padrao: DIRIGINDO)`

        Raises:
            `e`: Erros da api

        Returns:
            `dict`: Detalhes sobre o endereco mais proximo
        """       
        _res = self._proximo_de(endereco, modo)
        res = self._clean_results(_res)
        retorno = min(res, key=lambda d:d[0])
        retorno = retorno[1] if retorno else None
        if retorno:        
            retorno['destino'] = next(filter(lambda e: e['LOGRADOURO'] in retorno['destino'], self.ubs_ends))
        
        return retorno
        
        
    def _clean_results(self, results):
        
        apenas_ok = lambda x: filter(lambda x: x['status'] == 'OK', x)
        
        for resposta in results:
            for resultado in apenas_ok(resposta):
                yield resultado['distance']['value'], resultado
          
    def _proximo_de(self, endereco:str, modo:Modos)->dict:                 
        # Monta o endereco de busca LOGRADOURO + BAIRRO   
        ends = list(map(lambda x: f"{x['LOGRADOURO']} {x['BAIRRO']}",self.ubs_ends))
        
        pcts_dest = self._pacotes_ends(ends=ends, max=25)        
        try:  
            for pacote_dest in pcts_dest:          
                resposta =  self.maps.distance_matrix(origins=endereco,destinations=pacote_dest, mode=modo, language=self.lang)                            
                _resultados = resposta['rows'][0]['elements']                
                # Conecta destino ao retorno da api
                for res_api, dest in zip(_resultados, pacote_dest):
                    res_api['destino'] = dest                    
                yield _resultados
        except Exception as e:            
            match str(e):
                case 'Invalid travel mode.':
                    raise "Modo invalido"
            raise e        
    
    def _pacotes_ends(self, ends:list[str], max:int):  
        """ Separa pacotes no tamanho limite para requisicao."""                   
        for i in range(0, len(ends), max):
            yield ends[i:i+max]
    
