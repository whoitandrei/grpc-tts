#include "MainWindow.h"

#include <QAudioOutput>
#include <QBoxLayout>
#include <QDir>
#include <QFile>
#include <QFileDialog>
#include <QFormLayout>
#include <QJsonDocument>
#include <QJsonObject>
#include <QLabel>
#include <QLineEdit>
#include <QMessageBox>
#include <QIODevice>
#include <QNetworkReply>
#include <QNetworkRequest>
#include <QPushButton>
#include <QSaveFile>
#include <QStandardPaths>
#include <QTextEdit>
#include <QUrl>
#include <QWidget>
#include <QComboBox>
#include <QSlider>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent),
      audioOutput_(new QAudioOutput(this)),
      positionSlider_(new QSlider(Qt::Horizontal, this))
{
    player_.setAudioOutput(audioOutput_);
    audioOutput_->setVolume(1.0);

    buildUi();
    setAudioReady(false);

    connect(&network_, &QNetworkAccessManager::finished,
            this, &MainWindow::handleSynthesizeFinished);
    connect(&player_, &QMediaPlayer::playbackStateChanged,
            this, &MainWindow::updatePlaybackState);
    connect(&player_, &QMediaPlayer::errorOccurred,
            this, &MainWindow::showPlaybackError);
    connect(&player_, &QMediaPlayer::durationChanged, this, [=](qint64 duration) {
        positionSlider_->setRange(0, duration);
    });
    connect(&player_, &QMediaPlayer::positionChanged, this, [=](qint64 position) {
        if (!positionSlider_->isSliderDown())
            positionSlider_->setValue(position);
    });
    connect(positionSlider_, &QSlider::sliderMoved, this, [=](int position) {
        player_.setPosition(position);
    });

}

void MainWindow::buildUi()
{
    setWindowTitle("TTS Qt Client");

    auto *central = new QWidget(this);
    auto *rootLayout = new QVBoxLayout(central);

    auto *formLayout = new QFormLayout();
    apiUrlEdit_ = new QLineEdit("http://127.0.0.1:8000/synthesize", central);
    voiceCombo_ = new QComboBox(central);
    voiceCombo_->addItem("default");

    langCombo_ = new QComboBox(central);
    langCombo_->addItem("en");


    formLayout->addRow("API URL:", apiUrlEdit_);
    formLayout->addRow("Голос:", voiceCombo_);
    formLayout->addRow("Язык:", langCombo_);

    textEdit_ = new QTextEdit(central);
    textEdit_->setPlaceholderText("Введите текст, который нужно озвучить...");

    sendButton_ = new QPushButton("Синтезировать", central);
    playButton_ = new QPushButton("Прослушать", central);
    stopButton_ = new QPushButton("Стоп", central);
    pauseButton_ = new QPushButton("Пауза", central);
    saveButton_ = new QPushButton("Сохранить WAV", central);
    statusLabel_ = new QLabel("Готово к использованию", central);
    statusLabel_->setWordWrap(true);

    auto *buttonLayout = new QHBoxLayout();
    buttonLayout->addWidget(sendButton_);
    buttonLayout->addWidget(playButton_);
    buttonLayout->addWidget(stopButton_);
    buttonLayout->addWidget(pauseButton_);
    buttonLayout->addWidget(saveButton_);
    buttonLayout->addStretch();

    rootLayout->addLayout(formLayout);
    rootLayout->addWidget(new QLabel("Запрос:", central));
    rootLayout->addWidget(textEdit_, 1);
    rootLayout->addWidget(positionSlider_);
    rootLayout->addLayout(buttonLayout);
    rootLayout->addWidget(statusLabel_);

    setCentralWidget(central);

    connect(sendButton_, &QPushButton::clicked, this, &MainWindow::synthesize);
    connect(playButton_, &QPushButton::clicked, this, &MainWindow::playAudio);
    connect(stopButton_, &QPushButton::clicked, this, &MainWindow::stopAudio);
    connect(pauseButton_, &QPushButton::clicked, this, &MainWindow::pauseAudio);
    connect(saveButton_, &QPushButton::clicked, this, &MainWindow::saveAudio);
}

void MainWindow::synthesize()
{
    const QString text = textEdit_->toPlainText().trimmed();
    const QUrl apiUrl(apiUrlEdit_->text().trimmed());

    if (text.isEmpty()) {
        QMessageBox::warning(this, "Пустой запрос", "Введите текст для синтеза.");
        return;
    }

    if (!apiUrl.isValid() || apiUrl.scheme().isEmpty()) {
        QMessageBox::warning(this, "Некорректный URL", "Введите полный URL API, например http://127.0.0.1:8000/synthesize.");
        return;
    }

    clearUnsavedAudio();
    setBusy(true);
    setStatus("Отправляю запрос...");

    QJsonObject payload;
    payload["text"] = text;
    payload["voice"] = voiceCombo_->currentText().trimmed().isEmpty()
        ? QString("default")
        : voiceCombo_->currentText().trimmed();
    payload["language"] = langCombo_->currentText().trimmed().isEmpty() 
        ? QString("en")
        : langCombo_->currentText().trimmed();

    QNetworkRequest request(apiUrl);
    request.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");
    request.setRawHeader("Accept", "audio/wav");

    network_.post(request, QJsonDocument(payload).toJson(QJsonDocument::Compact));
}

void MainWindow::handleSynthesizeFinished(QNetworkReply *reply)
{
    reply->deleteLater();
    setBusy(false);

    if (reply->error() != QNetworkReply::NoError) {
        setAudioReady(false);
        setStatus("Ошибка запроса: " + reply->errorString());
        return;
    }

    const QByteArray audio = reply->readAll();
    if (audio.isEmpty()) {
        setAudioReady(false);
        setStatus("Сервис вернул пустой аудиофайл.");
        return;
    }

    QScopedPointer<QTemporaryFile> tempFile(new QTemporaryFile(QDir::tempPath() + "/tts-client-XXXXXX.wav"));
    tempFile->setAutoRemove(true);

    if (!tempFile->open()) {
        setAudioReady(false);
        setStatus("Не удалось создать временный WAV-файл.");
        return;
    }

    tempFile->write(audio);
    tempFile->flush();
    tempFile->close();

    audioFile_.swap(tempFile);
    audioSaved_ = false;
    player_.setSource(QUrl::fromLocalFile(audioFile_->fileName()));
    setAudioReady(true);
    setStatus("Аудио готово. Можно прослушать или сохранить.");
}

void MainWindow::playAudio()
{
    if (!audioFile_) {
        return;
    }

    player_.play();
}

void MainWindow::pauseAudio()
{
    player_.pause();
}

void MainWindow::stopAudio()
{
    player_.stop();
}

void MainWindow::saveAudio()
{
    if (!audioFile_) {
        return;
    }

    QString defaultDir = QStandardPaths::writableLocation(QStandardPaths::MusicLocation);
    if (defaultDir.isEmpty()) {
        defaultDir = QDir::homePath();
    }

    const QString targetPath = QFileDialog::getSaveFileName(
        this,
        "Сохранить WAV",
        defaultDir + "/tts-result.wav",
        "WAV audio (*.wav)");

    if (targetPath.isEmpty()) {
        return;
    }

    QFile source(audioFile_->fileName());
    QSaveFile target(targetPath);

    if (!source.open(QIODevice::ReadOnly)
            || !target.open(QIODevice::WriteOnly)
            || target.write(source.readAll()) == -1
            || !target.commit()) {
        QMessageBox::critical(this, "Ошибка сохранения", "Не удалось сохранить аудиофайл.");
        return;
    }

    audioSaved_ = true;
    setStatus("Файл сохранен: " + targetPath);
}

void MainWindow::updatePlaybackState(QMediaPlayer::PlaybackState state)
{
    pauseButton_->setEnabled(state == QMediaPlayer::PlayingState);
}

void MainWindow::showPlaybackError()
{
    if (player_.error() == QMediaPlayer::NoError) {
        return;
    }

    setStatus("Ошибка воспроизведения: " + player_.errorString());
}

void MainWindow::setBusy(bool busy)
{
    sendButton_->setEnabled(!busy);
    apiUrlEdit_->setEnabled(!busy);
    voiceCombo_->setEnabled(!busy);
    textEdit_->setEnabled(!busy);
    langCombo_->setEnabled(!busy);
}

void MainWindow::setAudioReady(bool ready)
{
    playButton_->setEnabled(ready);
    saveButton_->setEnabled(ready);
    stopButton_->setEnabled(ready);
    pauseButton_->setEnabled(false);
}

void MainWindow::clearUnsavedAudio()
{
    player_.stop();
    player_.setSource(QUrl());

    if (audioFile_ && !audioSaved_) {
        setStatus("Предыдущий временный файл удален.");
    }

    audioFile_.reset();
    audioSaved_ = false;
    setAudioReady(false);
}

void MainWindow::setStatus(const QString &message)
{
    statusLabel_->setText(message);
}