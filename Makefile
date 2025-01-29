include .env

tmp_dir := ./tmp
params := $(wildcard ./parameters/*.json)
hack := ${tmp_dir}/Hack-Regular.ttf ${tmp_dir}/Hack-Bold.ttf
mgenplus := ${tmp_dir}/mgenplus-1m-regular.ttf ${tmp_dir}/mgenplus-1m-bold.ttf
nerd_font_patcher := ${tmp_dir}/FontPatcher.zip
nerd := ${tmp_dir}/NerdFont.ttf

define delete
    @if [ -d ${1} ]; then \
	    echo "Dir '${1}' deleted."; \
        rm -rf ${1}; \
	elif [ -e ${1} ]; then \
		echo "File '${1}' deleted."; \
		rm ${1}; \
    else \
        echo "'${1}' not found."; \
    fi

endef

${hack}: .env
	@curl -fsL https://github.com/source-foundry/Hack/releases/download/${HACK_VERSION}/Hack-${HACK_VERSION}-ttf.zip -o ${tmp_dir}/hack.zip
	@unar -f ${tmp_dir}/hack.zip -o ${tmp_dir}/hack
	@cp ${tmp_dir}/hack/ttf/Hack-Regular.ttf ${tmp_dir}
	@cp ${tmp_dir}/hack/ttf/Hack-Bold.ttf ${tmp_dir}

${mgenplus}: .env
	@curl -fsL https://ftp.iij.ad.jp/pub/osdn.jp/users/8/8597/mgenplus-${MGENPLUS_VERSION}.7z -o ${tmp_dir}/mgenplus.7z
	@unar -f ${tmp_dir}/mgenplus.7z -o ${tmp_dir} 
	@cp ${tmp_dir}/mgenplus/mgenplus-1m-regular.ttf ${tmp_dir}
	@cp ${tmp_dir}/mgenplus/mgenplus-1m-bold.ttf ${tmp_dir}

${nerd_font_patcher}: .env
	@curl -fsL https://github.com/ryanoasis/nerd-fonts/releases/download/${NERD_VERSION}/FontPatcher.zip -o ${tmp_dir}/FontPatcher.zip
	@unar -f ${tmp_dir}/FontPatcher.zip -o ${tmp_dir} 

${nerd}: ${nerd_font_patcher}
	@python3 -m src.build_nerd --src-dir ${tmp_dir}/FontPatcher/src/glyphs --dst-dir ${tmp_dir}
	@cd ./previews; python3 ../src/export_html.py .${nerd} > NerdFont.html

.PHONY: nerd
nerd:
	@$(call delete,${nerd})
	@make ${nerd}

.PHONY: build
build: ${hack} ${mgenplus} ${nerd}
	@$(foreach param, ${params}, \
		python3 -m src.build_pennywort --src-dir ${tmp_dir} ${param}; \
	)

	@$(eval fonts := $(wildcard ./dist/*.ttf))
	@cd ./previews; $(foreach font, ${fonts}, \
		$(eval name := $(subst ./dist/,,${font})) \
		$(eval name := $(subst .ttf,,${name})) \
		python3 ../src/export_html.py .${font} > ${name}.html; \
	)

.PHONY: shell
shell:
	@docker run -it --rm --env-file=.env -v .:/app pennywort /bin/bash