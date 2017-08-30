# [Meetup Churrops] - Iniciando a trilha com o Vault - Hands-on


### Apresentação e considerações

* Este projeto tem como objetivo apresentar de forma prática o Vault da HashiCorp
* A configuração/orquestração do ambiente será realizado através do Ansible, que terá como objetivo preparar 2 containers:

    * 1 MySQL
    * 1 Vault Server

* Após a configuração teremos um ambiente totalmente disponível para realização dos exemplos que teremos logo abaixo
* O ambiente foi configurado na Amazon AWS em um instância t2.micro, porém é possível que você execute em outros players de Cloud ou até mesmo em seu ambiente local.

### O que é o Vault HashiCorp?

O Vault nada mais é que uma ferramenta para acessar de forma segura os "secrets".
Um secret pode ser qualquer coisa que você deseja controlar o acesso, como chaves, API's, senhas, certificados e etc.

O Vault fornece uma interface unificada para qualquer secret, proporcionando um controle de acesso totalmente seguro e com um registro de auditoria bem detalhado.

Escrito em Go (linguagem criada pelo Google) e distribuído em um único binário, é possível realizar sua instação com poucos comandos

Uma vez que que o binário esteja em seu ambiente, basta executar os comandos, possibilitando a configuração de um client/server

### Orquestrando o ambiente

* Configurando o ambiente (AWS ou OpenStack)

Passo 1 - Clone do projeto
<pre>
$ git clone https://github.com/vandocouto/Vault-Meetup-Churrops.git
</pre>

Passo 2 - Acessando o projeto 
<pre>
$ cd Vault-Meetup-Churrops/ansible/vault/
</pre>
Passo 3 - Configurando o arquivo hosts<br>
* No arquivo hosts você deverá informar o ip da instância (AWS - OpenStack) - Ubuntu 16.04<br>
* No meu exemplo o ip da instância é 54.172.229.173
<pre>
[vault]
54.172.229.173

[all:vars]
# EC2
ansible_ssh_user=ubuntu
ansible_ssh_private_key_file=../../keys/vault.pem

# SSL
fqdn=tutoriaisgnulinux.com
</pre>
Passo 4 - Preparando a instância para "rodar" o playbook
* Neste passo, será instalado via ansible o pacote python-simplejson.

<pre>
$ ansible 54.172.229.173 -i hosts -m 'raw apt-get -y install python-simplejson' -b
</pre>
Passo 5 - Ansible playbook 
<pre>
$ ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i hosts ./tasks/main.yml
</pre>
## Vault na prática

### Configurando o ambiente

Passo 6 - Criando a variável de dentro da instância EC2    
<pre>
$ export VAULT_ADDR=https://127.0.0.1:8200
</pre>
Passo 7 - Criando a variável no ambiene local

<pre>
$ export VAULT_ADDR=https://54.172.229.173:8200
</pre>

### keys - token - sealed - unseal

* Durante inicialização (vault init) as chaves de criptografia serão geradas (chaves unseal e o token de root inicial)
* Esta é a única vez que todos esses dados são conhecidos pelo Vault
* É necessário que guarde todas essas chaves em um local seguro, distribuindo em ambientes diferentes<br>
* Quando o Vault é resselado (“sealed"), reiniciado, ou parado, você deverá fornecer pelo menos 3 chaves para que ele volte ao estado ("desselado") unseal

Passo 8 - Inicialização - Vault init 

<pre>
$ vault init -tls-skip-verify
Unseal Key 1: QLBm12RW4diu7AEwzLW6V7WkEHA9/7OktJ2YcqZ3Vz15
Unseal Key 2: tdjpuYHFi+GNSv/CIZ5hC1WppjFKuBt5toeADGYIe9Ex
Unseal Key 3: qz/cKss9B91ueRtBqfkvy5zDsltQB774nr8FNNcyqv6R
Unseal Key 4: blbft5ofQXphq/3mwPm9uwQ705Oc/+qB+eRQdP5Kwamn
Unseal Key 5: KWNKH3BuSxqLodN0YxuPnLEh/3nMOIaFpp/yeNKD+qKD
Initial Root Token: cbbfb448-60ab-22f8-c585-afa4e6aed339

Vault initialized with 5 keys and a key threshold of 3. Please
securely distribute the above keys. When the vault is re-sealed,
restarted, or stopped, you must provide at least 3 of these keys
to unseal it again.

Vault does not store the master key. Without at least 3 keys,
your vault will remain permanently sealed.
</pre>

### Inserindo as chaves 
 
Passo 9 - Chave 1 e Chave 2
<pre> 
<b>evandrocouto@desktop:~$</b> vault unseal -tls-skip-verify QLBm12RW4diu7AEwzLW6V7WkEHA9/7OktJ2YcqZ3Vz15
Sealed: true
Key Shares: 5
Key Threshold: 3
Unseal Progress: 1

Unseal Nonce: 6b2fb500-bb6a-bdc7-2817-f3d5857d2407
<b>evandrocouto@desktop:~$</b> vault unseal -tls-skip-verify tdjpuYHFi+GNSv/CIZ5hC1WppjFKuBt5toeADGYIe9Ex
Sealed: true
Key Shares: 5
Key Threshold: 3
Unseal Progress: 2
Unseal Nonce: 6b2fb500-bb6a-bdc7-2817-f3d5857d2407

<b>root@ip-10-0-0-111:/home/ubuntu#</b> vault unseal -tls-skip-verify qz/cKss9B91ueRtBqfkvy5zDsltQB774nr8FNNcyqv6R
Sealed: false
Key Shares: 5
Key Threshold: 3
Unseal Progress: 0
Unseal Nonce: 
</pre>
Passo 11 - Chave 3
<pre>
$vault unseal -tls-skip-verify
Key (will be hidden): 
Sealed: false
Key Shares: 5
Key Threshold: 3
Unseal Progress: 0
Unseal Nonce: 
</pre>

Bingo!

<pre>
<b>evandrocouto@desktop:~$</b> vault unseal -tls-skip-verify
Vault is already unsealed.
</pre>

* O processo unseal é totalmente stateful, possibilitando que através de outro computador com o Vault instalado, possa executar o processo de desbloqueio (unseal),<br>
isso quanto o Vault estiver direcionado para o mesmo Vault Server.<br>

* Isso é extremamente importante para o processo de unseal. Somente assim, duas ou mais pessoas poderão liberar o Vault.<br>
 
* O Vault pode ser "aberto" de vários computadores e as chaves nunca deverão estarem juntas.<br>
* Desta forma, um único operador não possuirá chaves suficientes para ser mal-intencionado.

### Vault Auth 

* Uma vez que o ambiente esteja unseal, o passo seguinte será o comando vault auth, que terá como função autenticar-se no Vault com o token root.
* Com o token root, será possível fechar o Vault (Único operador que poderá fazer isso). 
* Isso permite que um único operador bloqueie o Vault em uma emergência sem consultar os demais operadores.
* Qaundo o Vault é selado (sealed) novamente, ele limpa todo o estado (incluindo a chave de criptografia) da memória.

Passo 12 - vault auth
<pre>
$ vault auth -tls-skip-verify 
Token (will be hidden): 
Successfully authenticated! You are now logged in.
token: 11fbbd18-3e55-e49d-f949-0148c6bb0c87
token_duration: 0
token_policies: [root]
</pre>

### Primeiro Secret

* Para criar o primeiro secret, basta utilizar o comando vault write,<br>
informando o path.

Passo 13 - vault write
<pre>
$ vault write -tls-skip-verify secret/hello value=world 
Success! Data written to: secret/hello
</pre>

### Lendo um secret

* O Vault lê os dados do armazenamento e em seguida desencriptografa-os. 
* O formato de saída é propositadamente separado em espaços em branco para facilitar a utilização de ferramentas como cut, awk, grep e etc.
* Além do formato do Vault, é possível também utilizar ferramentas como o jq (apt-get Install jq), podendo enviar os dados no formato JSON. 

Passo 14 - vault read
<pre>
$ vault read -tls-skip-verify secret/hello 
Key             	Value
---             	-----
refresh_interval	768h0m0s
value           	world
</pre>

Passo 15 - vault read (json)
<pre>
vault read -tls-skip-verify -format=json secret/hello
{
	"request_id": "55814798-f9bc-9740-594f-a862d8e76e87",
	"lease_id": "",
	"lease_duration": 2764800,
	"renewable": false,
	"data": {
		"value": "world"
	},
	"warnings": null
}
</pre>
Passo 16 - vault read (json + jq)
<pre>
$ vault read -tls-skip-verify -format=json secret/hello | jq -r .data.value
world
</pre>

### Excluindo um secret

* Para excluir um secret, basta utilizar o comando vault delete.

Passo 17 - vault delete
<pre>
$ vault delete -tls-skip-verify secret/hello
Success! Deleted 'secret/hello' if it existed.
</pre>

### Backends secret (secret/prefix) 

* Para que seja possível escrever os secrets no Vault é necessário especificar qual o backend que pretende utilizar. 
* Por padrão, o Vault monta um backend chamado de genérico.
* O backend lê e grava os dados no Storage Backend.
* O Vault suporte outros tipos de backends, além do genérico, e esse recurso em particular é o que torna o Vault exclusivo.
* O Vault se comporta como um sistema de arquivos: Os backends são montados em caminhos específicos (backend/prefix).


##### Alguns backend suportados:

    * CockroachDB
    * Consul 
    * DynamoDB
    * Etcd
    * Filesystem
    * Google Cloud
    * In-Memory
    * Mysql
    * PostrgreSQL
    * Cassandra
    * S3
    * Swift
    * Zookeper

### Mount Backend
* Assim como em um sistema de arquivos normal, o Vault pode montar um backend várias vezes em diferentes pontos de montagem.
* Também é importante saber que com o Vault é possível aplicar politicas de segurança através de caminhos diferentes.

Passo 18 - vault mounts (list)
<pre>
$ vault mounts -tls-skip-verify
Path        Type       Accessor            Plugin  Default TTL  Max TTL  Force No Cache  Replication Behavior  Description
cubbyhole/  cubbyhole  cubbyhole_3d283166  n/a     n/a          n/a      false           local                 per-token private secret storage
secret/     generic    generic_61fb4a37    n/a     system       system   false           replicated            generic secret storage
sys/        system     system_997f9d46     n/a     n/a          n/a      false           replicated            system endpoints used for control, policy and debugging
</pre>

Passo 19 - vault mount (create)
<pre>
$ vault mount -tls-skip-verify generic
Successfully mounted 'generic' at 'generic'!
</pre>

Passo 20 - vault mount (list)
<pre>
$ vault mounts -tls-skip-verify
Path        Type       Accessor            Plugin  Default TTL  Max TTL  Force No Cache  Replication Behavior  Description
cubbyhole/  cubbyhole  cubbyhole_3d283166  n/a     n/a          n/a      false           local                 per-token private secret storage
generic/    generic    generic_baf5911b    n/a     system       system   false           replicated            
secret/     generic    generic_61fb4a37    n/a     system       system   false           replicated            generic secret storage
sys/        system     system_997f9d46     n/a     n/a          n/a      false           replicated            system endpoints used for control, policy and debugging
</pre>

### Unmount backend
* Uma vez que o backend for desmontado, todos os seus secrets serão revogados e seus dados excluídos.

Passo 21 - vault unmount 
<pre>
$ vault unmount -tls-skip-verify generic 
Successfully unmounted 'generic' if it was mounted
</pre>

### Vault Token 
* Você pode criar mais tokens usando o vault token-create
* Por padrão, o Vault token criará um token filho do seu token atual (pai) que herdará todos as mesmos direitos (políticas).
<pre>
$ vault token-create -tls-skip-verify
Key            	Value
---            	-----
token          	ee3afb8f-152d-3178-0fdc-c97ea03111f3
token_accessor 	8fa5e81f-71ad-27ca-d104-e69bba49891e
token_duration 	0s
token_renewable	false
token_policies 	[root]
</pre>

* Depois que um token é criado, é possível revogá-lo com o token-revoke.

<pre>
$ vault token-revoke -tls-skip-verify ee3afb8f-152d-3178-0fdc-c97ea03111f3
Success! Token revoked if it existed.
</pre>

### Auth Backends

* Além dos tokens, é possível também adicionar outros métodos de autenticação. 
* Auth backends permite métodos alternativos de identificação com o Vault. 
* Essas identidades são vinculadas de volta a um conjunto de políticas de acesso, assim como tokens. 

Passo 22 - Habilitando o método de autenticação pelo GitHub
<pre>
$ vault auth-enable -tls-skip-verify github
Successfully enabled 'github' at 'github'!
</pre>
Passo 23 - Criando o secret/prefix e fixando a organização do GitHub
<pre>
$ vault write -tls-skip-verify auth/github/config organization=tutoriaisgnulinux
Success! Data written to: auth/github/config
</pre>
Passo 24 - Por fim, com o comando vault auth, basta informar o token gerado no GitHub para obter acesso no Vault.
<pre>
$  vault auth -tls-skip-verify -method=github token=1a014ecc8e71d2938abba8d8d8830fd71dd052cd
Successfully authenticated! You are now logged in.
The token below is already saved in the session. You do not
need to "vault auth" again with the token.
<b>token: 17229894-200b-80aa-f8af-e9ec813f7100</b>
token_duration: 2764800
token_policies: [default]
</pre>
Passo 25 - Para revogar a autenticação 
<pre>
$ vault token-revoke -tls-skip-verify -mode=path auth/github
Success! Token revoked if it existed.
</pre>
Passo 26 - Desativando o backend
<pre>
$ vault auth-disable -tls-skip-verify github
</pre>
### Policys 

* As policys do Vault controlam os acessos dos usuários.
* Para autenticação, o Vault possui várias opções ou backends que podem ser ativados e usados. 
* Para autorização e políticas (policys), o Vault sempre usa o mesmo formato.
* Todos os backends de autenticação devem mapear as identidades de volta para as políticas principais configuradas com o Vault.
* Ao inicializar o Vault, sempre existe uma política (policy) especial que não pode ser removida: (root).
* Está politica (policy) é uma política especial que lhe dará o acesso de super-user em tudo que há no Vault. 
* Uma identidade mapeada para a diretiva root pode fazer qualquer coisa. 
* As políticas do Vault controlam o acesso do usuário.
* Para autenticação, o Vault possui várias opções ou backends que podem ser ativadas e usadas. 
* Para autorização e políticas, o Vault sempre usa o mesmo formato. 
* Todos os backends de autenticação devem mapear identidades de volta para as políticas principais configuradas com o Vault.
* Ao inicializar o Vault, sempre existe uma política especial que não pode ser removida: a política raiz. 
* Esta política é uma política especial que lhe dá acesso de superusuário a tudo no Vault. 
* Uma identidade mapeada para a diretiva raiz pode fazer qualquer coisa.
* As políticas (policys) no Vault são criadas no formato HCL. 
* O HCL é um formato de configuração legível para humanos e também é compatível com o formato JSON.

##### Exemplo:
<pre>
ath "secret/*" {
  capabilities = ["create"]
}

path "secret/foo" {
  capabilities = ["read"]
}

path "auth/token/lookup-self" {
  capabilities = ["read"]
}
</pre>

Passo 27 - vault auth token root 

<pre>
vault auth -tls-skip-verify
Token (will be hidden): 
Successfully authenticated! You are now logged in.
token: ba3534bd-cadc-5520-30f9-c51449ec29c6
token_duration: 0
token_policies: [root]

</pre>
Passo 28 - Listando as policys 

<pre>
$ vault read -tls-skip-verify sys/policy
Key     	Value
---     	-----
keys    	[default root]
policies	[default root]
</pre>

### Criando policys

Passo 29 - Acesse o diretório policys
<pre>
$ cd policys/
</pre>
Passo 30 - Criando a policy meetup
<pre>
$ vault write -tls-skip-verify sys/policy/meetup rules=@meetup.hcl
Success! Data written to: sys/policy/meetup
</pre>
Passo 31 - Criando a policy github
<pre>
$ vault write -tls-skip-verify sys/policy/github rules=@github.hcl
Success! Data written to: sys/policy/github
</pre>
Passo 32 - Lendo a estrutura da policy<br>
meetup
<pre>
$ vault read -tls-skip-verify sys/policy/meetup
Key  	Value
---  	-----
name 	meetup
rules	path "secret/meetup" {
  capabilities = ["create", "read", "update", "delete", "list"]
}
</pre>
github
<pre>
$ vault read -tls-skip-verify sys/policy/github
Key  	Value
---  	-----
name 	github
rules	path "secret/github/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}
</pre>

### Mapeando policys para outros Backends

Passo 33 - Novamente acessando o Vault com o token do GitHub
<pre>
$ vault auth -tls-skip-verify -method=github token=1a014ecc8e71d2938abba8d8d8830fd71dd052cd
Successfully authenticated! You are now logged in.
The token below is already saved in the session. You do not
need to "vault auth" again with the token.
token: 17229894-200b-80aa-f8af-e9ec813f7100
token_duration: 2764800
token_policies: [default]
</pre>
Passo 34 - Criando um novo secret no path secret/github "hello" com o valor "world"
<pre>
$ vault write -tls-skip-verify secret/github/hello value=world
Error writing data to secret/github/hello: Error making API request.

URL: PUT https://127.0.0.1:8200/v1/secret/github/hello
Code: 403. Errors:

<b>* permission denied</b>
</pre>
#### ERROR!

#### Resolvendo o problema

Passo 35 - Mapeando a indentidade (github) para o token do GitHub. 

<pre>
$ vault write -tls-skip-verify auth/github/map/teams/default value=github
Success! Data written to: auth/github/map/teams/default
</pre>

Passo 36 - Novamente com o token do GitHub.

<pre>
$ vault auth -tls-skip-verify -method=github token=1a014ecc8e71d2938abba8d8d8830fd71dd052cd
Successfully authenticated! You are now logged in.
The token below is already saved in the session. You do not
need to "vault auth" again with the token.
token: 996b80c8-7bc5-b67f-2aad-80796bdcf821
token_duration: 2764800
token_policies: [default <b>github</b>]
</pre>

PAsso 37 - Escrevendo no secret/github com o token do GitHub.
<pre>
$ vault write -tls-skip-verify secret/github/hello value=world
Success! Data written to: secret/github/hello
</pre>
#### Bingo!

### Brincando com os tokens

Passo 38 - Autenticando com o token root
<pre>
vault auth -tls-skip-verify
Token (will be hidden): 
Successfully authenticated! You are now logged in.
token: ba3534bd-cadc-5520-30f9-c51449ec29c6
token_duration: 0
token_policies: [root]
</pre>
Passo 39 - Criando o token para a policy meetup
<pre>
$ vault token-create -tls-skip-verify -policy=meetup
Key            	Value
---            	-----
<b>token          	45f823ce-fc72-8ca1-f8f0-9c9f4e38078d</b>
token_accessor 	0cd5d109-1976-5791-2882-32fd03c48a36
token_duration 	768h0m0s
token_renewable	true
token_policies 	[default meetup]
</pre>
Passo 40 - Acessando com o token criado para policy meetup
<pre>
$ vault auth -tls-skip-verify
Token (will be hidden): 
Successfully authenticated! You are now logged in.
token: 45f823ce-fc72-8ca1-f8f0-9c9f4e38078d
token_duration: 2764641
token_policies: [default meetup]
</pre>
Passo 41 - Escrevendo no secret/meetup 

<pre>
vault write -tls-skip-verify <b>secret/meetup</b> value=world
Success! Data written to: secret/meetup
</pre>
Passo 41 - Escrevendo no secret/meetup e criando um novo prefix com o valor world
#### ERROR!
<pre>
vault write -tls-skip-verify secret/meetup/teste value=world
Error writing data to secret/meetup/teste: Error making API request.

URL: PUT https://127.0.0.1:8200/v1/secret/meetup/teste
Code: 403. Errors:

* permission denied
</pre>

* Não foi possivel pelo fato da policy (meetup.hcl) não permitir que seja criado novos prefix.
<pre>
path "secret/meetup" {
  capabilities = ["create", "read", "update", "delete", "list"]
}
</pre>

* Para resolver, basta alterar o arquivo (meetup.hcl), inserindo o /*.
<pre>
path "secret/meetup/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}
</pre>
Passo 42 - Ajustando novamente a policy
<pre>
$ vault write -tls-skip-verify sys/policy/meetup rules=@meetup.hcl
Success! Data written to: sys/policy/meetup
</pre>
Passo 43 - Testando novamente com o token do meetup
<pre>
$ vault write -tls-skip-verify secret/meetup/teste value=world
Success! Data written to: secret/meetup/teste
</pre>

### Vault e AWS

Backend  secret AWS

* Com o Backend AWS é possível gerir as credenciais de acesso no Amazon AWS dinamicamente bom base nas políticas IAM.
* As credenciais podem ser geradas facilmente, podendo ser revogadas quando a concessão (lease) do Vault expirar.

Passo 44 - Montando o backend aws. <br>
Obs: Ao contrário do backend genérico, o backend da Aws não é montado por padrão.
<pre>
$ vault mount -tls-skip-verify aws
Successfully mounted 'aws' at 'aws'!
</pre>

Passo 45 - Em seguida, será preciso informar as credenciais (AWS) que o Vault usuará para gerenciar o IAM

<pre>
$ vault write -tls-skip-verify aws/config/root access_key="$AWS_ACCESS_KEY_ID" secret_key="$AWS_SECRET_ACCESS_KEY" region="us-east-1"
Success! Data written to: aws/config/root
</pre>

Passo 46 - Neste passo será necessário importar o arquivo iam-policy.json

* Isso é usado para criar dinamicamente um novo par de credenciais IAM quando necessário.
* A policy será carregada através do arquivo chamado iam-policy.json.

<pre>
 cat iam-policy.json 
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "iam:*",
      "Resource": "*"
    }
  ]
}
</pre>

* Function: Nome lógico que será mapeado para uma policy, usado para gerenciar as credenciais.
* Por exemplo: Criando a function "dev" através da policy inline:

<pre>
$ vault write -tls-skip-verify aws/roles/dev policy=@iam-policy.json
Success! Data written to: aws/roles/dev
</pre>

##### Criando dinamicamente um par de credenciais IAM, quando necessário.

Passo 46 - Para gerar um novo conjunto de credenciais IAM, bastar ler executar a function abaixo:

<pre>
$ vault read -tls-skip-verify aws/creds/dev
Key            	Value
---            	-----
lease_id       	aws/creds/dev/a6ef57b6-1187-1ca1-4f11-6bfafe9fb642
lease_duration 	768h0m0s
lease_renewable	true
access_key     	AKIAJMZFG5PAZ5EPFS7Q
secret_key     	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
security_token 	<nil>
</pre>
Passo 47 - Caso execute novamente, será criado um novo conjunto de credenciais
<pre>
$ vault read -tls-skip-verify aws/creds/dev
Key            	Value
---            	-----
lease_id       	aws/creds/dev/a6ef57b6-1187-1ca1-4f11-6bfafe9fb642
lease_duration 	768h0m0s
lease_renewable	true
access_key     	AKIAJZ5YRPHFH3QHRRRQ
secret_key     	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
security_token 	<nil>
</pre>

Passo 48 - Neste outro exemplo, será cria uma function "de leitura" usando uma nova policy AWS

<pre>
$ vault write -tls-skip-verify aws/roles/readonlyec2 arn=arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess
Success! Data written to: aws/roles/readonlyec2
</pre>
Passo 49 - Para gerar o conjunto de chaves IAM, bastar ler executar a function readonlyec2

<pre>
$ vault read -tls-skip-verify aws/creds/readonlyec2
Key            	Value
---            	-----
lease_id       	aws/creds/readonlyec2/675a475f-3adf-ef3c-3de5-936b8f7d736b
lease_duration 	3m0s
lease_renewable	true
access_key     	AKIAJTTKWCRXB3QE2JLA
secret_key     	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
security_token 	<nil>
</pre>

Passo 50 - Criando um policy para o prefix ec2rdsfull, carregando a policy do arquivo ec2rdsfull.json
<pre>
$ cd policys
$ vault write -tls-skip-verify aws/roles/ec2rdsfull policy=@ec2rdsfull.json
</pre>
Passo 51 - Gerando o access_key e o secret_key

Obs: A policy ec2rdsfull irá conceder a permissão Full para EC2 e RDS. 
<pre>
$ vault read -tls-skip-verify aws/creds/ec2rdsfull
Key            	Value
---            	-----
lease_id       	aws/creds/ec2rdsfull/aefcc6f6-59e9-5be1-cdfa-4b89432a0b73
lease_duration 	3m0s
lease_renewable	true
access_key     	AKIAJ3BCNUC6X2SYYACA
secret_key     	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
security_token 	<nil>
</pre>

### Lease, Renew, and Revoke

* Por segurança o Vault guarda por um determinado período as informações em metadados contendo a duração do tempo, renovabilidade e muito mais de um secret.
* O Vault precisa garantir que os dados serão válidos durante a duração que foi determinado (TTL). 
* Uma vez que aquele arrendamento do secret expirou, o Vault pode revogar automaticamente os dados, e com isso o consumidor não poderá mais ter certeza que aquela informação do secret seja válida.
* Após revogados, os consumidores dos secrets precisam fazer o check-in no Vault para renovar o contrato de arrendamento (caso permitido). 
* Isso faz com que os logs de auditoria do Vault sejam mais valiosos e também tornando a chave muto mais fácil.
* Todos os secrets dinâmicos no Vault são obrigados a terem um contrato de arrendamento. 
* Quando uma locação for revogada, o secret imediatamente será invalidado para evitar novas renovações.

* Exemplo:<br>
  * Com o backend secret da AWS, as chaves de acesso serão excluídas da AWS no momento em que o secret for revogado.Isso tornará as chaves de acesso inválida a partir desse ponto.

* OBs: Com o Backend (Generic Backend Storage) com os secret arbitrários não será possível trabalhar com o lease.

Passo 52 - Ajustando o lease do backend AWS.

<pre>
$ vault write -tls-skip-verify aws/config/lease lease=30s lease_max=5m
Success! Data written to: aws/config/lease
</pre>

Passo 53 - Verificando as alterações
<pre>
$ vault read -tls-skip-verify aws/creds/dev
Key            	Value
---            	-----
lease_id       	aws/creds/dev/d9dfa5d0-bc22-3677-0063-55ed1ebd1fa0
lease_duration 	<b>30s</b>
lease_renewable	true
access_key     	AKIAJDAKPDF4ONFRF5FQ
secret_key     	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
security_token 	<nil>
</pre>

### Revogando backends 

Passo 54 - Revogando o backend AWS
<pre>
$ vault revoke -tls-skip-verify -prefix aws/
Success! Revoked the secret with ID 'aws/', if it existed.
</pre>
Passo 55 - Revogando o backend GitHub
<pre>
$  vault revoke -tls-skip-verify -prefix github/
Success! Revoked the secret with ID 'github/', if it existed.
</pre>

### Brincando com os scripts python (Using the HTTP APIs)

* No diretório scripts, contém dois arquivos (get - post) para testes do Vault via requests.
* Para executá-los, basta alterar as variáveis de ip, value e payload.

Post
<pre>
$ python post-secret_hello.py
</pre>
Get 
<pre>
$ python get-secret_hello.py
</pre>

Fonte:<br>
https://www.vaultproject.io

Blog:<br>
http://tutoriaisgnulinux.com








