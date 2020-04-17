set -e

if [ "$ENV" = 'DEV' ]; then
	echo "Running Development Server"
	exec python "hello.py"
elif [ "$ENV" = 'UNIT' ]; then
	echo "Running Unit Test"
	exec python "tests.py"
else
	echo "Running Production Server"
	exec uwsgi --http 0.0.0.0:9090 --wsgi-file hello.py \
		--callable app --stats 0.0.0.0:9191
fi
