include .env

tmp_dir := ./tmp
params := $(wildcard ./parameters/*.json)
hack := ${tmp_dir}/Hack-Regular.ttf ${tmp_dir}/Hack-Bold.ttf
bizud := ${tmp_dir}/BIZUDGothic-Regular.ttf ${tmp_dir}/BIZUDGothic-Bold.ttf
nerd_font_patcher := ${tmp_dir}/FontPatcher.zip
nerd := ${tmp_dir}/NerdFont.ttf
license_url := https://github.com/okenakt/Pennywort/blob/main/LICENSE.txt

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

${bizud}: .env
	@curl -fsL https://github.com/googlefonts/morisawa-biz-ud-gothic/releases/download/${BIZUD_VERSION}/BIZUDGothic.zip -o ${tmp_dir}/bizud.zip
	@unar -f ${tmp_dir}/bizud.zip -o ${tmp_dir} 
	@cp ${tmp_dir}/bizud/BIZUDGothic-Regular.ttf ${tmp_dir}
	@cp ${tmp_dir}/bizud/BIZUDGothic-Bold.ttf ${tmp_dir}

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
build: ${hack} ${bizud} ${nerd}
	@$(foreach param, ${params}, \
		python3 -m src.build_pennywort \
		--src-dir ${tmp_dir} \
		--version ${VERSION} \
		--copyright-file ./COPYRIGHT.txt \
		--license-url ${license_url} \
		${param}; \
	)

	@cd ./previews; $(foreach param, ${params}, \
 		$(eval name := $(subst .json,,$(subst ./parameters/,,${param}))) \
		 python3 ../src/export_html.py ../dist/${name}.ttf > ${name}.html; \
	)

.PHONY: shell
shell:
	@docker run -it --rm --env-file=.env -v .:/app pennywort /bin/bash