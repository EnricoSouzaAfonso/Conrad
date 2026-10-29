import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() => runApp(const MaterialApp(
      home: TabuadaApp(),
      debugShowCheckedModeBanner: false,
    ));

class TabuadaApp extends StatefulWidget {
  const TabuadaApp({super.key});

  @override
  State<TabuadaApp> createState() => _TabuadaAppState();
}

class _TabuadaAppState extends State<TabuadaApp> {
  int _fator = 2;
  int _multiplicador = 1;
  String _resposta = '';

  @override
  void initState() {
    super.initState();
    _carregar();
  }

  void _carregar() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _fator = prefs.getInt('fator') ?? 2;
      _multiplicador = prefs.getInt('multiplicador') ?? 1;
    });
  }

  void _salvar() async {
    final prefs = await SharedPreferences.getInstance();
    prefs.setInt('fator', _fator);
    prefs.setInt('multiplicador', _multiplicador);
  }

  void _verificar() {
    if (_resposta.isEmpty) return;

    if (int.tryParse(_resposta) == _fator * _multiplicador) {
      if (_multiplicador < 10) {
        _multiplicador++;
      } else {
        _fator++;
        _multiplicador = 1;
      }
    } else {
      int anterior = _fator;
      _fator++;
      _multiplicador = 1;

      ScaffoldMessenger.of(context).clearSnackBars();
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('Errou!'),
          action: SnackBarAction(
            label: 'Clique aqui para continuar',
            onPressed: () {
              setState(() => _fator = anterior);
              _salvar();
            },
          ),
        ),
      );
    }

    setState(() => _resposta = '');
    _salvar();
  }

  @override
  Widget build(BuildContext context) {
    final botoes = [
      '1',
      '2',
      '3',
      '4',
      '5',
      '6',
      '7',
      '8',
      '9',
      'C',
      '0',
      'OK'
    ];

    return Scaffold(
      appBar:
          AppBar(title: const Text('Jogo da Multiplicação'), centerTitle: true),
      body: Center(
        child: SizedBox(
          width: 320,
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                LinearProgressIndicator(value: _multiplicador / 10),
                const SizedBox(height: 24),
                Text(
                  '$_fator x $_multiplicador = ${_resposta.isEmpty ? "?" : _resposta}',
                  style: const TextStyle(
                      fontSize: 36, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 24),
                GridView.count(
                  crossAxisCount: 3,
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  mainAxisSpacing: 10,
                  crossAxisSpacing: 10,
                  childAspectRatio: 1.4,
                  children: botoes.map((t) {
                    return ElevatedButton(
                      onPressed: () {
                        if (t == 'C') {
                          setState(() => _resposta = '');
                        } else if (t == 'OK') {
                          _verificar();
                        } else {
                          setState(() => _resposta += t);
                        }
                      },
                      child: Text(t, style: const TextStyle(fontSize: 20)),
                    );
                  }).toList(),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}