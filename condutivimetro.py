# ---------------------------------------------------------
#   ANALISE DOS DADOS EXPERIMENTAIS CONDUTIVIMETRO
# ---------------------------------------------------------
#
# DATA: 2024.03.29
#
# LUCAS PIMENTA DOS SANTOS MONTEIRO
#
# OBJETIVOS DO PROGRAMA: 
# -> TRATAR OS DADOS OBTIDOS POR MEIO DO ARQUIVO .CSV GERADO NO SOFTWARE DA AGILENT
# -> TRATAR OS DADOS OBTIDOS POR MEIO DO .CSV DA MEDIÇÃO DA AMOSTRA ANALISADA
# -> ESTIMAR A CONDUTIVIDADE TERMICA DA AMOSTRA
#
# FORMATO DOS ARQUIVOS .CSV:
#
# -> ARQUIVO CSV DO AGILENT -> FORMATO ORIGINAL DO ARQUIVO
# -> ARQUIVO CSV DAS MEDIDAS DE ESPESSURA DA AMOSTRA -> EM CADA LINHA O VALOR DE UMA MEDICAO USANDO PONTO COMO SEPARADOR DECIMAL
#
# EXEMPLO DO ARQUIVO .CSV DAS MEDIDAS DA AMOSTRA:
#
# 20.15
# 20.10
# 20.20
#
#   INSTALANDO AS BIBLIOTECAS
#
import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
#
install("flet")
install("pandas")
install("dash")
#
# IMPORTANDO BIBLIOTECAS
#
import flet as ft # FRONT END -> INSTERFACE DO USUARIO
import pandas as pd # TRATAMENTO DE DADOS E LEITURA E GRAVACAO DOS ARQUIVOS .CSV
from time import sleep
import threading
from dash import dcc, html, Dash
import webbrowser
#
# DEFININDO E INICIALIZANDO VARIAVEIS GLOBAIS
#
path_file_agilent = ""
path_file_amostra = ""
r_paquimetro = 0
variacao_rp_temp = 0
variacao_rp_fluxo = 0
k = 0
inc_k = 0
global_df_agilent = None
data_analise = None
tempo_analise_rp = None
#
# DEFINICAO DA JANELA DE INTERFACE
#
def main (page: ft.Page):
    page.title = "Análise Condutivímetro"
    page.window_height = 300
    page.window_width = 600
    page.padding = 18
    page.window_center()
    page.update()  
    #
    # DEFININDO AS ROTAS DE TELA DO APLICATIVO
    #
    def route_change(route):
        #page.views.clear()
        #
        # PRIMEIRA PAGINA -> ESCOLHENDO O CAMINHO DO ARQUIVO .CSV DO AGILENT
        # FUNCAO PARA OBTER O NOME DO ARQUIVO E O CAMINHO DE ACORDO COM A RESPOSTA DO GERENCIADOR DE ARQUIVOS
        #
        def on_dialog_result(e: ft.FilePickerResultEvent):
            #
            # O RESULTADO DO PICK_FILES É UMA LISTA COM META DADOS DE CADA ARQUIVO SELECIONADO
            # NAO ESTA HABILITADA A SELECAO DE MULTIPLOS ARQUIVOS, MESMO ASSIM, POR SEGURANCA OCORRE A SELECAO DO PRIMEIRO ITEM DA LISTA
            # E SUA CONVERSAO EM TEXTO
            #
            resultado = str(e.files[0])
            #
            # CRIACAO DE UMA SUBSTRING APENAS CONTENDO O NOME DO ARQUIVO
            #
            file_name = resultado[resultado.index("=")+1:resultado.index(",")]
            #
            # A STRING DO RESULTADO É ATUALIZADA RETIRANDO A PARTE JA COLETADA DO NOME DO ARQUIVO
            #
            resultado = resultado[resultado.index(",")+2:]
            #
            # CRIACAO DE UMA SUBSTRING APENAS CONTENDO O CAMINHO DO ARQUIVO
            #
            file_path = resultado[resultado.index("=")+1:resultado.index(",")]
            #
            # VERIFICANDO QUAL FOI O ARQUIVO SELECIONADO
            #
            file_path = file_path.strip("'")
            file = open(file_path, "r")
            if ":" in file.readline():
                # AGILENT
                global path_file_agilent
                path_file_agilent = file_path
                b_navegate_check_1.tooltip = path_file_agilent
                b_navegate_check_1.on_click = lambda _: file_picker.pick_files(allowed_extensions=["csv"])
                b_navegate1.visible = False
                b_navegate_check_1.visible = True
                b_navegate2.disabled = False
            else:
                # AMOSTRA
                global path_file_amostra
                path_file_amostra = file_path
                b_navegate_check_2.tooltip = path_file_amostra
                b_navegate_check_2.on_click = lambda _: file_picker.pick_files(allowed_extensions=["csv"])
                b_navegate2.visible = False
                b_navegate_check_2.visible = True
                b_navegate3.disabled = False
            file.close()
            page.update()   
        #
        # DEFININDO O FILE PICKER
        #
        file_picker = ft.FilePicker(on_result=on_dialog_result)
        page.overlay.append(file_picker)
        #
        # DEFININDO MENSAGEM INICIAL DO PROGRAMA
        #
        text1 = ft.Text(value= "Após Selecionar os Dados Clique em Prosseguir", size=18)
        #    
        # DEFININDO O TEXTO A SER EXIBIDO DO LADO DO BOTAO
        #
        text2 = ft.Text(value= "Selecione o arquivo .csv obtido pelo software da Agilent",size= 14)
        text3 = ft.Text(value= "Selecione o arquivo .csv obtido pela medição da amostra", size= 14)
        text4 = ft.Text(value= "Selecione a resolução do paquímetro utilizado", size= 14)
        text5 = ft.Text(value= "Selecione a variação aceitável da temperatura para regime permanente", size= 14)
        text6 = ft.Text(value= "Selecione a variação aceitável do fluxo de calor para regime permanente", size= 14)
        text7 = ft.Text(value= "O valor da condutividade do material analisado em W/m.K é:", size= 18)
        #
        # DEFININDO O BOTAO PARA SELECIONAR O ARQUIVO
        #
        b_navegate1 = ft.OutlinedButton(text="Selecionar Arquivo", on_click=lambda _: file_picker.pick_files(allowed_extensions=["csv"]), tooltip = "O arquivo deve estar no formato original do Agilent")
        b_navegate2 = ft.OutlinedButton(text="Selecionar Arquivo", on_click=lambda _: file_picker.pick_files(allowed_extensions=["csv"]), tooltip = "O arquivo deve conter uma medição em mm por linha, com '.' no delimitador decimal")
        b_navegate3 = ft.FilledTonalButton(text="Prosseguir", width= 800, on_click=lambda _: page.go("/definicao"))
        b_navegate4 = ft.FilledTonalButton(text="Analisar", width= 800, on_click=lambda _: button_clicked())
        #
        # CONFIGURANDO OS ICONES DE RESPOSTA APOS A ESCOLHA DOS ARQUIVOS
        #
        b_navegate_check_1 = ft.IconButton(icon=ft.icons.CHECK_CIRCLE_OUTLINE, icon_color="blue400", icon_size=20)
        b_navegate_check_1.visible = False
        b_navegate_check_2 = ft.IconButton(icon=ft.icons.CHECK_CIRCLE_OUTLINE, icon_color="blue400", icon_size=20)
        b_navegate_check_2.visible = False
        #
        # PARA MAIS ICONES BASTA ACESSAR O LINK ABAIXO
        # https://gallery.flet.dev/icons-browser/
        #
        # POSICIONANDO O TEXTO E BOTAO LADO A LADO
        #
        conteudo_1 = ft.Column([text1, ft.Row([text2, b_navegate1, b_navegate_check_1],spacing=15), ft.Row([text3, b_navegate2, b_navegate_check_2]), b_navegate3], spacing= 30)
        #
        # DEFININDO OS STATUS DOS BOTOES
        #
        b_navegate2.disabled = True
        b_navegate3.disabled = True
        #
        # DEFININDO DROP DOWN
        #
        dd_1 = ft.Dropdown(width=90,text_size=12, height= 47,options=[ft.dropdown.Option("0.01mm"),ft.dropdown.Option("0.05mm"),ft.dropdown.Option("0.1mm"),ft.dropdown.Option("0.2mm"),ft.dropdown.Option("0.5mm")])
        dd_2 = ft.Dropdown(width=90,text_size=12, height= 47,options=[ft.dropdown.Option("0.1°C"),ft.dropdown.Option("0.2°C"),ft.dropdown.Option("0.3°C"),ft.dropdown.Option("0.5°C"),ft.dropdown.Option("1°C"),ft.dropdown.Option("2°C"),ft.dropdown.Option("3°C")])
        dd_3 = ft.Dropdown(width=90,text_size=12, height= 47,options=[ft.dropdown.Option("0.5%"),ft.dropdown.Option("1%"),ft.dropdown.Option("2%"),ft.dropdown.Option("3%"),ft.dropdown.Option("4%"),ft.dropdown.Option("5%"),ft.dropdown.Option("10%")])
        #
        conteudo_2 = ft.Column([ft.Row([text4, dd_1],spacing=177), ft.Row([text5, dd_2],spacing=20), ft.Row([text6, dd_3]), b_navegate4], spacing= 20)
        #
        page.views.append(ft.View("/home",[conteudo_1]))
        #
        # SEGUNDA PAGINA
        #
        if page.route == "/definicao":
            #page.views.append(ft.View("/store",[ft.ElevatedButton("Go Home", on_click=lambda _: page.go("/home")), dd_1]))
            def button_clicked():
                global r_paquimetro
                global variacao_rp_temp
                global variacao_rp_fluxo
                r_paquimetro = float(dd_1.value[:-2])
                variacao_rp_temp = float(dd_2.value[:-2])
                variacao_rp_fluxo = float(dd_3.value[:-1])/100          # DIVIDI POR 100 PARA FICAR EM PORCENTAGEM
                page.update()
                page.go("/loading")
            page.views.append(ft.View("/definicao",[conteudo_2]))
        if page.route == "/loading":
            #page.views.append(ft.View("/store",[ft.ElevatedButton("Go Home", on_click=lambda _: page.go("/home")), dd_1]))
            global done
            done = False
            def animate():
                global done
                pb = ft.ProgressBar(width=400)
                text_loading = ft.Text("Analisando", style="headlineSmall", text_align= "CENTER")
                loading_bar = ft.ProgressBar(width=400, color="Blue400", bgcolor="#eeeeee")
                page.views.append(ft.View("/loading",[text_loading,loading_bar], vertical_alignment= ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER))
                page.update()
                for i in range(0, 10100):                    # ADICIONEI UM ZERO NO LIMITE SUPERIOR POR CAUSA DO FOR, CASO CONTRARIO A TRANSICAO DE PAGINA NAO OCORRE
                    if done:
                        page.go("/resultado")
                        break
                    pb.value = i * 0.01
                    sleep(0.1)
                    page.update()
            t = threading.Thread(target=animate)
            t.start()
            # ------------------------------------------------------------------------------------------------------------
            #
            #                                   INICIO DA ANALISE DE DADOS
            #
            # ------------------------------------------------------------------------------------------------------------
            #
            # EXTRAINDO OS DADOS DO ARQUIVO DA AMOSTRA
            file = open(path_file_amostra, "r", encoding= 'utf-8')
            df_amostra = pd.DataFrame(file)
            file.close()
            for p, line in enumerate(df_amostra[0]):
                df_amostra[0].iloc[p] = str(df_amostra[0].iloc[p]).strip()
            df_amostra[0] = df_amostra[0].astype(float)
            e = (df_amostra[0].mean())*(10**(-3))
            #
            #
            # EXTRAINDO OS DADOS DO ARQUIVO DO AGILENT
            file = open(path_file_agilent, "r", encoding= 'utf-16')
            df_agilent = pd.DataFrame(file)
            file.close()
            last_row = len(df_agilent)-1
            df_agilent = df_agilent.drop([0,1,2,3,4,5,6,7,8,9,10,11,12,last_row]) # RETIRANDO O CABECALHO E A ULTIMA LINHA QUE GERALMENTE E VAZIA
            last_row = len(df_agilent)-1
            df_agilent = df_agilent[0].str.split(',', expand=True) # SEPARANDO A COLUNA UNICA EM MULTIPLAS COLUNAS COM O DELIMITADOR ","
            df_agilent = df_agilent[[0,1,2,4,6]] # SELECIONANDO APENAS AS COLUNAS COM DADOS RELEVANTES
            df_agilent.columns = ['medicao','data_hora', 'temp_1', 'temp_2', 'fluxo'] # RENOMEANDO AS COLUNAS
            #
            # MANIPULACAO DAS DATAS E HORAS
            #
            df_agilent['data_hora'] = df_agilent['data_hora'].str.slice(stop=-4)
            global data_analise
            data_analise = df_agilent['data_hora'].iloc[0][:10]
            df_agilent['data_hora'] = pd.to_datetime(df_agilent['data_hora'])
            intervalo_coleta = (df_agilent['data_hora'].iloc[1]-df_agilent['data_hora'].iloc[0]).total_seconds()
            #
            # CRIANDO NOVAS COLUNAS
            #
            df_agilent[['variacao_temp_1', 'variacao_temp_2', 'variacao_fluxo', 'tempo_s', 'tempo_h']] = 0.00 # INICIALIZANDO AS COLUNAS AUXILIAREM PARA FILTRAR O RP
            df_agilent['temp_1'] = df_agilent['temp_1'].astype(float)
            df_agilent['temp_2'] = df_agilent['temp_2'].astype(float) 
            df_agilent['fluxo'] = df_agilent['fluxo'].astype(float)
            for p,line in enumerate(df_agilent['variacao_temp_1']): # PREENCHENDO AS VARIACOES
                if p != len(df_agilent):
                    df_agilent['variacao_temp_1'].iloc[p] = abs(df_agilent.iloc[-1][2] - df_agilent.iloc[p][2])
                    df_agilent['variacao_temp_2'].iloc[p] = abs(df_agilent.iloc[-1][3] - df_agilent.iloc[p][3])
                    df_agilent['variacao_fluxo'].iloc[p] = abs(df_agilent.iloc[-1][4] - df_agilent.iloc[p][4])/df_agilent.iloc[-1][4]
                    df_agilent['tempo_s'].iloc[p] = p*intervalo_coleta # tem que resolver
                    horas = (df_agilent['tempo_s'].iloc[p])/3600
                    df_agilent['tempo_h'].iloc[p] =  horas #"{:.1f}".format(horas)
            #
            # FILTRANDO
            #
            # OUTPUT
            #
            #df_agilent.to_csv('output_2.csv')
            #
            # SALVANDO O DATAFRAME ORIGINAL (ANTES DE FILTRAR) PARA PLOTAR O GRAFICO COMPLETO
            #
            global global_df_agilent
            global_df_agilent = df_agilent
            filtro = (df_agilent['variacao_temp_1'] <= variacao_rp_temp) & (df_agilent['variacao_temp_2'] <= variacao_rp_temp) & (df_agilent['variacao_fluxo'] <= variacao_rp_fluxo)
            df_agilent = df_agilent[filtro]
            media_temp_1 = df_agilent['temp_1'].mean()
            media_temp_2 = df_agilent['temp_2'].mean()
            media_fluxo = df_agilent['fluxo'].mean()

            delta_t = media_temp_1 - media_temp_2

            # Lei de Fourier
            # q = -k (delta T / espessura) -> K = - q (espessura / delta T)
            # 
            global k
            k = (media_fluxo * (e/(delta_t)))
            k = "{:.3f}".format(k)
            #
            #
            # PROPAGACAO DE INCERTEZA

            # INCERTEZAS DO FORNECEDOR

            inc_f_espessura = 2*r_paquimetro*(10**(-3))
            inc_f_fluxo = 0.05*media_fluxo   # A INCERTEZA DE CALIBRACAO ENTRA AQUI?
            inc_f_delta_temperatura = (2**(0.5))*0.064

            # INCERTEZAS DO DESVIO PADRAO (k=2, POR ESSE MOTIVO O DESVIO PADRAO FOI MULTIPLICADO POR 2 EM QUASE TODOS OS CASOS EXCETO DESV_P_E)

            t_distribution_95 = {'1' :'12.69','2' :'4.271','3' :'3.179','4' :'2.776','5' :'2.570','6' :'2.447','7' :'2.365','8' :'2.306','9' :'2.262','10' :'2.228','11' :'2.201','12' :'2.179','13' :'2.160','14' :'2.145','15' :'2.131','16' :'2.120','17' :'2.110','18' :'2.101','19' :'2.093','20' :'2.086','21' :'2.080','22' :'2.074','23' :'2.069','24' :'2.064','25' :'2.060','26' :'2.056','27' :'2.052','28' :'2.048','29' :'2.045','30' :'2.042','40' :'2.021','50' :'2.009','60' :'2.000','70' :'1.994','80' :'1.990','90' :'1.987','100' :'1.984'}
            gl = str(len(df_amostra[0])-1)
            desv_p_e = float(t_distribution_95[gl])*(df_amostra[0].std())*(10**(-3))  # T STUDENT
            desv_p_fluxo = 2*(df_agilent["fluxo"].std())
            desv_p_delta_t = (df_agilent["temp_1"].std() + df_agilent["temp_2"].std())

            # COMBINANDO AS INCERTEZAS

            inc_espessura = inc_f_espessura + desv_p_e
            inc_fluxo = inc_f_fluxo + desv_p_fluxo
            inc_delta_temperatura = inc_f_delta_temperatura + desv_p_delta_t

            # DERIVADAS PARCIAIS

            dp_k_fluxo = - e/delta_t
            dp_k_e = - media_fluxo/delta_t
            dp_k_delta_t = (media_fluxo * e)/(delta_t**2)

            # PROPAGACAO DE INCERTEZA DO K
            global inc_k
            fator_1 = (dp_k_fluxo**2)*(inc_fluxo**2)
            fator_2 = (dp_k_e**2)*(inc_espessura**2)
            fator_3 = (dp_k_delta_t**2)*(inc_delta_temperatura**2)
            inc_k = ((fator_1 + fator_2 + fator_3)**0.5)
            inc_k = "{:.3f}".format(inc_k)
            # TEMPO DE ANALISE
            global tempo_analise_rp
            tempo_analise_rp = intervalo_coleta*len(df_agilent['temp_1'])
            #
            # ------------------------------------------------------------------------------------------------------------
            #
            #                                   FIM DA ANALISE DE DADOS
            #
            # ------------------------------------------------------------------------------------------------------------
            done = True
            # CRIANDO O APLICATIVO DASH
            def create_dash_app(df_agilent):
                app = Dash(__name__)
                # LAYOUT DASHBOARD
                app.layout = html.Div([
                html.H1("Análise Condutivímetro"),
                # ADICIONANDO COMPONENTES
                #
                # GRAFICO 1 -> TEMPERATURAS EM FUNCAO DO TEMPO
                #
                dcc.Graph(id='example-graph',
                        figure={'data': [{
                              'x': df_agilent['tempo_h'], 
                              'y': df_agilent['temp_1'], 
                              'type': 'line',
                              'name': 'Temperatura 1'},
                              {'x': df_agilent['tempo_h'], 
                               'y': df_agilent['temp_2'], 
                               'type': 'line', 
                               'name': 'Temperatura 2'},],
                               'layout': {'title': 'Temperatura x Tempo', 'xaxis': dict(title="Tempo [h]"),'yaxis': dict(title="Temperatura [°C]")}}),
                #
                # GRAFICO 2 -> FLUXO EM FUNCAO DO TEMPO
                #
                dcc.Graph(id='example-graph-2',
                        figure={'data': [{
                            'x': df_agilent['tempo_h'], 
                            'y': df_agilent['fluxo'], 
                            'type': 'line', 
                            'name': 'Fluxo de Calor'},],
                            'layout': {'title': 'Fluxo x Tempo', 'xaxis': dict(title="Tempo [h]"),'yaxis': dict(title="Fluxo [W]") }})                
                               ])
                return app
            dash_app = create_dash_app(global_df_agilent)
            # INICIANDO O SERVIDOR NO LOCALHOST 127.0.0.1
            dash_app.run_server(host='127.0.0.1', port=8050, debug=False)
            sleep(2)
        if page.route == "/resultado":
            tempo_rp_h = tempo_analise_rp // 3600          
            tempo_analise_rp = tempo_analise_rp % 3600
            tempo_rp_min = tempo_analise_rp // 60                                  # SEPARANDO APENAS A DIVISAO INTEIRA
            tempo_rp_s = tempo_analise_rp % 60                                     # SEPARANDO O RESTO DA DIVISAO
            tempo_rp_formatado = "{} horas, {} minutos e {} segundos".format(tempo_rp_h, tempo_rp_min, tempo_rp_s)
            tempo_rp_titulo = " Tempo em Regime Permanente "
            condutividade_titulo = " Valor da Condutividade "
            condutividade = "k = {} ± {} W/m.K".format(k, inc_k) 
            texto_rp_titulo = ft.Text(tempo_rp_titulo, size=16, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_700)
            texto_tempo_rp = ft.Text(tempo_rp_formatado, size=14)
            texto_condutividade_titulo = ft.Text(condutividade_titulo, size=16, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_700)
            texto_resultado = ft.Text(condutividade, size=14)
            conteudo_3 = ft.Column([texto_rp_titulo,texto_tempo_rp,texto_condutividade_titulo,texto_resultado], horizontal_alignment= ft.CrossAxisAlignment.CENTER, spacing=20)
            page.views.append(ft.View("/resultado",[conteudo_3], vertical_alignment= ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER))
            # ABRINDO O NAGEVADOR COM A URL DO APLICATIVO
            webbrowser.open_new('http://127.0.0.1:8050/')
        page.update()
    #
    #
    page.on_route_change = route_change
    page.go(page.route)
    #
ft.app(target=main)