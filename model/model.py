from database.impianto_DAO import ImpiantoDAO

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._impianti = None
        self.load_impianti()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_impianti(self):
        """ Carica tutti gli impianti e li setta nella variabile self._impianti """
        self._impianti = ImpiantoDAO.get_impianti()

    def get_consumo_medio(self, mese:int):
        """
        Calcola, per ogni impianto, il consumo medio giornaliero per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome dell'impianto, media), es. (Impianto A, 123)
        """
        # TODO
        risultati = []

        if self._impianti is None:
            print("❌ Nessun impianto caricato.")
            return risultati

        for imp in self._impianti:
            # Assicuriamoci di avere la lista consumi aggiornata
            imp.get_consumi()
            consumi = imp.lista_consumi or []

            # Filtra i consumi per il mese richiesto
            valori_mese = []
            for c in consumi:
                # c.data potrebbe essere stringa o oggetto date; cerchiamo di parsearlo
                try:
                    if isinstance(c.data, str):
                        data_obj = datetime.fromisoformat(c.data)
                    else:
                        data_obj = c.data
                except Exception:
                    # tentativo alternativo di parsing
                    try:
                        data_obj = datetime.strptime(str(c.data), "%Y-%m-%d")
                    except Exception:
                        continue

                if data_obj.month == mese:
                    try:
                        valori_mese.append(float(c.kwh))
                    except Exception:
                        pass

            media = 0.0
            if len(valori_mese) > 0:
                media = sum(valori_mese) / len(valori_mese)

            risultati.append((imp.nome, round(media, 2)))

        return risultati
    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di interventi nei primi 7 giorni
        :return: sequenza di nomi impianto ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        consumi_settimana = self.__get_consumi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, consumi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {impianto.id: impianto.nome for impianto in self._impianti}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, self.__costo_ottimo

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_impianto, costo_corrente, consumi_settimana):
        """ Implementa la ricorsione """
        # TODO
        if giorno > 7:
            if self.__costo_ottimo == -1 or costo_corrente < self.__costo_ottimo:
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima = sequenza_parziale.copy()
            return
        for imp in self._impianti:
            id_imp = imp.id
            try:
                costo_energia = consumi_settimana.get(id_imp, [0] * 7)[giorno - 1]
            except Exception:
                costo_energia = 0.0
            costo_spostamento = 0.0
            if ultimo_impianto is not None and ultimo_impianto != id_imp:
                costo_spostamento = 5.0

            nuovo_costo = costo_corrente + costo_energia + costo_spostamento

            sequenza_parziale.append(id_imp)
            self.__ricorsione(sequenza_parziale, giorno + 1, id_imp, nuovo_costo, consumi_settimana)
            sequenza_parziale.pop()
    def __get_consumi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i consumi dei primi 7 giorni del mese selezionato per ciascun impianto.
        :return: un dizionario: {id_impianto: [kwh_giorno1, ..., kwh_giorno7]}
        """
        # TODO
        from datetime import datetime
        risultati = {}

        if self._impianti is None:
            return risultati

        for imp in self._impianti:
            imp.get_consumi()
            consumi = imp.lista_consumi or []

            giorno_to_kwh = {}
            for c in consumi:
                try:
                    if isinstance(c.data, str):
                        d = datetime.fromisoformat(c.data)
                    else:
                        d = c.data
                except Exception:
                    try:
                        d = datetime.strptime(str(c.data), "%Y-%m-%d")
                    except Exception:
                        continue
                if d.month == mese:
                    giorno_to_kwh[d.day] = float(c.kwh)


            lista_settimana = [giorno_to_kwh.get(day, 0.0) for day in range(1, 8)]
            risultati[imp.id] = lista_settimana

        return risultati
