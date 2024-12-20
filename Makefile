include .env

hack := ${SOURCE_FONTS_DIR}/Hack-Regular.ttf ${SOURCE_FONTS_DIR}/Hack-Bold.ttf
mgenplus := ${SOURCE_FONTS_DIR}/mgenplus-1m-regular.ttf ${SOURCE_FONTS_DIR}/mgenplus-1m-bold.ttf
nerd := ${SOURCE_FONTS_DIR}/NerdFont.ttf

${hack}: .env
	@curl -fsL https://github.com/source-foundry/Hack/releases/download/${HACK_VERSION}/Hack-${HACK_VERSION}-ttf.zip -o ./tmp/hack.zip
	@unar -f ./tmp/hack.zip -o ./tmp/hack
	@cp ./tmp/hack/ttf/Hack-Regular.ttf ${SOURCE_FONTS_DIR}
	@cp ./tmp/hack/ttf/Hack-Bold.ttf ${SOURCE_FONTS_DIR}

${mgenplus}: .env
	@curl -fsL https://ftp.iij.ad.jp/pub/osdn.jp/users/8/8597/mgenplus-${MGENPLUS_VERSION}.7z -o ./tmp/mgenplus.7z
	@unar -f ./tmp/mgenplus.7z -o ./tmp 
	@cp ./tmp/mgenplus/mgenplus-1m-regular.ttf ${SOURCE_FONTS_DIR}
	@cp ./tmp/mgenplus/mgenplus-1m-bold.ttf ${SOURCE_FONTS_DIR}

${nerd}: .env
	@curl -fsL https://github.com/ryanoasis/nerd-fonts/releases/download/${NERD_VERSION}/FontPatcher.zip -o ./tmp/FontPatcher.zip
	@unar -f ./tmp/FontPatcher.zip -o ./tmp 
	@python3 -m pennywort.generate_nerd --src-dir ./tmp/FontPatcher/src/glyphs --dst-dir ${SOURCE_FONTS_DIR}


.PHONY: download
download: ${hack} ${mgenplus} ${nerd}

.PHONY: build
build: download
	@python3 -m pennywort --src-dir ${SOURCE_FONTS_DIR} ./parameters/regular.json
	@python3 -m pennywort --src-dir ${SOURCE_FONTS_DIR} ./parameters/bold.json
	@python3 -m pennywort --src-dir ${SOURCE_FONTS_DIR} ./parameters/italic.json
	@python3 -m pennywort --src-dir ${SOURCE_FONTS_DIR} ./parameters/bold_italic.json

.PHONY: shell
shell:
	@docker run -it --rm --env-file=.env -v .:/app pennywort /bin/bash