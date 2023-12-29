git submodule init
git submodule update

cd Meower-Svelte
git switch selfhosted-client #temp

npm install
npm run build

rm -rf ../build/
mv dist ../build/
mv ../build/assets/* ../build/