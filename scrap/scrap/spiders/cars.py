import scrapy
from decimal import Decimal

class CarsSpider(scrapy.Spider):
    name = "cars"
    allowed_domains = ["seminovos.com.br"]
    start_urls = ["https://seminovos.com.br/carro?ordenarPor=5&page={}&ajax".format(i+1) for i in range(144, 800)]

    def parse(self, response):
        for anuncio in response.css('div.anuncio-container'):
            if not anuncio.css('div.ad-list').get() is None:
                continue
            stringPreco = anuncio.css('div.value h4 a::text').get()
            if stringPreco.lower().strip() == 'valor a combinar':
                continue

            detalhes = anuncio.css('div.card-detalhes')
            stringKilometragem = detalhes.css('div.kilometragem span::text').get()
            if stringKilometragem.lower().strip() == 'não informada':
                continue

            linkToPage = anuncio.css('div.card-body a::attr(href)').get()

            yield response.follow(linkToPage, callback=self.parsePage)
    
    def parsePage(self, response):
        info = response.css('section.info-topo')
        tipo = info.css('a[itemprop="bodyType"]::attr(title)').get()
        marca = info.css('a[itemprop="brand"]::attr(title)').get()
        modelo = info.css('a[itemprop="model"]::attr(title)').get()
        data = info.css('div.part-infos div.mr-1 span::text').get()

        conteudo = response.css('section.veiculo-conteudo')
        header = conteudo.css('div.part-marca-modelo-valor')
        descricao = header.css('span.desc::text').get().split('\n')[1]
        preco = float(header.css('span.valor::text').get().replace('.', '').replace(',', '.'))
        
        detalhes = conteudo.css('div.part-items-detalhes-icones')
        quilometragem = int(detalhes.css('div[title=Quilometragem] span.valor span::text').get().split(' ')[0].replace('.', ''))
        cambio = detalhes.css('div[title=Câmbio] span.valor span::text').get()
        ano = int(detalhes.css('div[title="Ano - Modelo"] span.valor span::text').get().split('/')[1])
        portas = int(detalhes.css('div[title=Portas] span.valor span::text').get())
        combustivel = detalhes.css('div[title=Combustível] span.valor span::text').get()
        troca = detalhes.css('div[title="Troca?"] span.valor span::text').get()
        cor = detalhes.css('div[title=cor] span.valor::text').get()

        acessorios = '&'.join(conteudo.css('ul.lista-acessorios li span::text').getall())
        
        sobre = conteudo.css('p.description-print::text').get().replace('\n', ' ').replace(',', '')

        if conteudo.css('div[id="veiculo-vendido"]').get() is None:
            vendido = 'Não'
        else:
            vendido = 'Sim'

        yield {
            'marca': marca,
            'modelo': modelo,
            'tipo': tipo,
            'descricao': descricao,
            'preco': preco,
            'quilometragem': quilometragem,
            'cambio': cambio,
            'ano': ano,
            'portas': portas,
            'combustivel': combustivel,
            'troca': troca,
            'cor': cor,
            'acessorios': acessorios,
            'sobre': sobre,
            'vendido': vendido,
            'data': data
        }