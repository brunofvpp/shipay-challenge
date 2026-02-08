# Shipay Back-End Engineer Challenge


## Questão 1

Comecaria a implementação pela responsabilidade central: validar se o endereço associado a um CNPJ coincide com o endereço retornado a partir de um CEP. É importante isolar as dependências externas e garantir que eventuais falhas nas APIs de terceiros não afetem a aplicação. Por isso, a solução terá adapters específicos para cada provedor. Eu criaria um serviço orquestrador responsável por receber o CNPJ e o CEP, coordenar as chamadas externas e aplicar a regra de comparação. Esse orquestrador dependeria de interfaces abstratas, podendo realizar troca ou evoluções de provedores sem alterar a lógica principal. Para garantir resiliência, eu utilizaria uma estratégia de retentativas automáticas com backoff exponencial, como um Circuit Breaker simplificado, evitando insistir em um serviço indisponível e reduzindo o tempo total de resposta, bem como as chamadas teriam timeouts para retornar uma falha rápida e previsível ao inves de aguardar indefinidamente, já que a resposta precisa ser síncrona. Após obter os dois resultados, eu normalizaria os dados antes da comparação para evitar variações de abreviações, acentuação e formatação.

Segue diagramas C4 até o 3 nível:

<a href="question_1/C4_Context.png" target="_blank">C4 Context</a>

<a href="question_1/C4_Container.png" target="_blank">C4 Container</a>

<a href="question_1/C4_Component.png" target="_blank">C4 Component</a>


## Questão 2

A solução é desacoplar a geração do relatório do fluxo de lançamento, fazendo com que falhas no novo processo não impacte o fluxo principal. Eu implementaria uma arquitetura baseada em eventos assíncronos com armazenamento paralelo. O endpoint de lançamento continua responsável pelo negócio principal, após registrar com sucesso o dado, ele publica um evento contendo os dados necessários para o relatório mas também utiliza transactional outbox para controle dos eventos emitidos. Essa publicação não deve ser bloqueante. Utilizaria um broker como Kafka, RabbitMQ ou SNS/SQS para receber eventos junto com a criação de dead letter queues para garantir que nenhum dado de relatório seja perdido em falhas críticas, as mensagens que falharem no worker podem ser enviadas para uma fila de erro para reprocessamento posterior. Criaria o serviço de ingestão do relatório que tem um worker que consome os eventos e grava em uma base paralela, desenhada para leitura agregada. Essa base até pode ter schemas desnormalizados por relatório para facilitar as consultas. O processamento inclui validação, enriquecimento e deduplicação idempotente para evitar contagens duplicadas como optimistic lock.

Segue diagramas C4 até o 2 nível:

<a href="question_2/C4_Context.png" target="_blank">C4 Context</a>

<a href="question_2/C4_Container.png" target="_blank">C4 Container</a>


## Questão 3

Eu usaria o Locust para realizar os seguintes testes:

  - Teste de carga com spawn rate de 50 users/s até atingir 1.000 rp/s para determinar se o requisito de performace está sendo atendido.
  - Teste de stress aumentando a carga gradualmente até encontrar o ponto de ruptura e determinar o limite de rp/s da aplicação.
  - Teste de estabilidade utilizando carga fixa de pelo menos 1000 rp/s por um periodo maior para determinar se a aplicação se mantem estavel sem degradar a performace.

O ideal seria rodar os testes em um ambiente o mais proximo possivel de produção. Com isso é possivel gerar os relatórios com: gráfico de P99, taxa de erro, throughput para cada um dos testes


## Questão 4

- Falta testes.

- Inconsistencia na tipagem apesar de não estar funcionando como strict, além de alguns contratos não estarem vinculados a classe abstrata criando alto acoplamento.

- Configuração fragmentada usando Base diferente cada parte pode usar metadatas diferentes.

- `Controller` tem acoplamento implícito com estrutura de request e depende de path param inexistente.

- `SqlRepository` e `RegistrationRepository` sofrem de fragmentação de sessao, apesar de funcional vão falhar silenciosamente, causando problema de DI e false UOW. Além do uso incorreto do selectinload.

- `Orchestrator` está fazendo bypass na camada de domínio usando o repository.

- `Tools` se tornou um God object com muitas responsabilidades além das queries feitas que estão propensas a sofrer SQL injection.

- `ExceptionHandlerMiddleware` está expondo o stacktrace, revelando o funcionamento interno da aplicação facilitando a engenharia reversa.


## Questão 5

[Implementacao aqui](./question_5/README.md)


## Questão 6

 - Falta testes.

 - O logger está com tamanho muito pequeno é necessario aumenta-lo pra diminuir a rotação de arquivos.

 - O config parser está apontando para o caminho errado, além de corrigir seria interessante implementar um fallback pra esse caso.

 - Muitos valores estão hardcoded, inclusive dados sensiveis sugiro criar env vars.

 - add_job irá falhar pois espera receber um callable.

 - A query sql tem o potencial de derrubar a aplicação por falta de memória se a tabela consultada for muito grande, sugiro deixar explicito na consulta somente os campos que serão utilizados e consumir os dados em chunks.

 - Caso dê erro de qualquer natureza o arquivo xlsx que está sendo criado, não será devidamente fechado, melhor caminho seria adicionar um try/finally.

 - Evitaria expor dados sensiveis como senha, além de deixar os usuarios vulneraveis a criação desse arquivo pode violar as normas da LGPD.

 - Como os relatórios gerados não estão sendo excluídos eventualmente a aplicação vai sofrer com falta de armazenagem, se possível criar usando `tempfile` ou envia-lós para storage externo.

 - Algumas variaveis estão com nomes improprios ou pouco descritivos.

 - Faz mais sentido utilizar o logger do que usar print.


## Questão 7

Eu utilizaria o padrão adapter junto com strategy e em alguns casos com factory. Assim cada serviço terá o seu adapter deixando o código fica desacoplado enquanto a lógica de cada serviço externo permanece isolada. Para facilitar o switch de adapter em tempo de execução sem mexer na lógica de negócio podemos usar Strategy e Factory para centralizar a criação sem ter que decidir manualmente qual Adapter instanciar em cada parte do código.
