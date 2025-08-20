#!/bin/bash

echo "🚀 CONFIGURAÇÃO GIT E PUBLICAÇÃO NA NUVEM"
echo "=========================================="
echo ""

# Verificar se Git está configurado
echo "🔍 Verificando configuração Git..."
if ! git config --global user.name > /dev/null 2>&1; then
    echo "❌ Git não está configurado. Vamos configurar agora:"
    echo ""
    
    # Solicitar informações do usuário
    read -p "Digite seu nome completo: " USER_NAME
    read -p "Digite seu email do GitHub: " USER_EMAIL
    
    # Configurar Git
    git config --global user.name "$USER_NAME"
    git config --global user.email "$USER_EMAIL"
    
    echo "✅ Git configurado com:"
    echo "   Nome: $USER_NAME"
    echo "   Email: $USER_EMAIL"
else
    echo "✅ Git já está configurado:"
    echo "   Nome: $(git config --global user.name)"
    echo "   Email: $(git config --global user.email)"
fi

echo ""
echo "📋 OPÇÕES DE PUBLICAÇÃO:"
echo "========================"
echo "1. GitHub (Recomendado)"
echo "2. GitLab"
echo "3. Bitbucket"
echo "4. Outro"
echo ""

read -p "Escolha sua plataforma (1-4): " PLATFORM

case $PLATFORM in
    1)
        echo ""
        echo "🐙 CONFIGURAÇÃO GITHUB"
        echo "======================"
        echo ""
        echo "Opções para criar repositório:"
        echo "1. Manual (você cria no site)"
        echo "2. GitHub CLI (se instalado)"
        echo ""
        
        read -p "Escolha opção (1-2): " GITHUB_OPTION
        
        if [ "$GITHUB_OPTION" = "1" ]; then
            echo ""
            echo "📝 INSTRUÇÕES MANUAIS:"
            echo "======================"
            echo "1. Acesse: https://github.com/new"
            echo "2. Nome do repositório: t031a5"
            echo "3. Descrição: Sistema AI multimodal para robô Unitree G1"
            echo "4. NÃO inicialize com README (já temos)"
            echo "5. Clique em 'Create repository'"
            echo ""
            
            read -p "Digite seu usuário do GitHub: " GITHUB_USER
            
            echo ""
            echo "🔗 Configurando repositório remoto..."
            git remote add origin https://github.com/$GITHUB_USER/t031a5.git
            
            echo "📤 Fazendo push..."
            git push -u origin main
            
            echo ""
            echo "✅ REPOSITÓRIO CRIADO!"
            echo "======================"
            echo "URL: https://github.com/$GITHUB_USER/t031a5"
            echo ""
            
        elif [ "$GITHUB_OPTION" = "2" ]; then
            echo ""
            echo "🔧 Verificando GitHub CLI..."
            if command -v gh &> /dev/null; then
                echo "✅ GitHub CLI encontrado!"
                echo "🔐 Fazendo login..."
                gh auth login
                
                echo "📦 Criando repositório..."
                gh repo create t031a5 --public --description "Sistema AI multimodal para robô Unitree G1" --source=. --remote=origin --push
                
                echo ""
                echo "✅ REPOSITÓRIO CRIADO!"
                echo "======================"
                echo "URL: https://github.com/$(gh api user --jq .login)/t031a5"
                echo ""
            else
                echo "❌ GitHub CLI não encontrado."
                echo "Instale com: brew install gh"
                echo "Ou use a opção manual (1)"
            fi
        fi
        ;;
        
    2)
        echo ""
        echo "🦊 CONFIGURAÇÃO GITLAB"
        echo "======================"
        echo ""
        read -p "Digite seu usuário do GitLab: " GITLAB_USER
        read -p "Digite a URL do GitLab (ex: gitlab.com): " GITLAB_URL
        
        echo "🔗 Configurando repositório remoto..."
        git remote add origin https://$GITLAB_URL/$GITLAB_USER/t031a5.git
        
        echo "📤 Fazendo push..."
        git push -u origin main
        
        echo ""
        echo "✅ REPOSITÓRIO CRIADO!"
        echo "======================"
        echo "URL: https://$GITLAB_URL/$GITLAB_USER/t031a5"
        echo ""
        ;;
        
    3)
        echo ""
        echo "🔵 CONFIGURAÇÃO BITBUCKET"
        echo "========================="
        echo ""
        read -p "Digite seu usuário do Bitbucket: " BITBUCKET_USER
        
        echo "🔗 Configurando repositório remoto..."
        git remote add origin https://bitbucket.org/$BITBUCKET_USER/t031a5.git
        
        echo "📤 Fazendo push..."
        git push -u origin main
        
        echo ""
        echo "✅ REPOSITÓRIO CRIADO!"
        echo "======================"
        echo "URL: https://bitbucket.org/$BITBUCKET_USER/t031a5"
        echo ""
        ;;
        
    4)
        echo ""
        echo "🌐 OUTRA PLATAFORMA"
        echo "==================="
        echo ""
        read -p "Digite a URL do repositório remoto: " REMOTE_URL
        
        echo "🔗 Configurando repositório remoto..."
        git remote add origin "$REMOTE_URL"
        
        echo "📤 Fazendo push..."
        git push -u origin main
        
        echo ""
        echo "✅ REPOSITÓRIO CRIADO!"
        echo "======================"
        echo "URL: $REMOTE_URL"
        echo ""
        ;;
        
    *)
        echo "❌ Opção inválida"
        exit 1
        ;;
esac

echo "🎉 CONFIGURAÇÃO CONCLUÍDA!"
echo "=========================="
echo "✅ Git configurado"
echo "✅ Repositório criado"
echo "✅ Código publicado"
echo ""
echo "📋 PRÓXIMOS PASSOS:"
echo "==================="
echo "1. Acesse o repositório no navegador"
echo "2. Verifique se todos os arquivos estão lá"
echo "3. Configure colaboradores se necessário"
echo "4. Continue desenvolvendo com: git add . && git commit -m 'msg' && git push"
echo ""
echo "🚀 Projeto t031a5 publicado com sucesso!"

