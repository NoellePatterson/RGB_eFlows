## Getting started

1. Install [Python3](https://www.python.org/downloads/), [Git](https://git-scm.com/download/) and a [text editor](https://www.sublimetext.com/3) of your choice.
2. Clone your project in [Terminal](http://www.informit.com/blogs/blog.aspx?uk=The-10-Most-Important-Linux-Commands)

   ```
   git clone https://github.com/NoellePatterson/RGB_eFlows.git
   cd RGB_eFlows/
   ```

3. Create and activate virtualenv
For Mac OS:
   ```
   python3 -m venv my-virtualenv
   source my-virtualenv/bin/activate
   ```
For Windows:
   ```
   python -m venv my-virtualenv
   my-virtualenv\Scripts\activate
   ```

5. Install dependencies

   ```
   pip install -r requirements.txt
   ```

6. Use raw csv outputs from the functional flows calculator to process RGB flow metrics