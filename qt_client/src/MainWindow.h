#pragma once

#include <QMainWindow>
#include <QMediaPlayer>
#include <QNetworkAccessManager>
#include <QScopedPointer>
#include <QTemporaryFile>

class QLabel;
class QLineEdit;
class QPushButton;
class QTextEdit;
class QAudioOutput;
class QNetworkReply;
class QComboBox;

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = nullptr);
    ~MainWindow() override = default;

private slots:
    void synthesize();
    void handleSynthesizeFinished(QNetworkReply *reply);
    void playAudio();
    void stopAudio();
    void saveAudio();
    void updatePlaybackState(QMediaPlayer::PlaybackState state);
    void showPlaybackError();

private:
    void buildUi();
    void setBusy(bool busy);
    void setAudioReady(bool ready);
    void clearUnsavedAudio();
    void setStatus(const QString &message);

    QNetworkAccessManager network_;
    QMediaPlayer player_;
    QAudioOutput *audioOutput_ = nullptr;

    QLineEdit *apiUrlEdit_ = nullptr;
    QTextEdit *textEdit_ = nullptr;
    QPushButton *sendButton_ = nullptr;
    QPushButton *playButton_ = nullptr;
    QPushButton *stopButton_ = nullptr;
    QPushButton *saveButton_ = nullptr;
    QLabel *statusLabel_ = nullptr;
    QComboBox *voiceCombo_ = nullptr;

    QScopedPointer<QTemporaryFile> audioFile_;
    bool audioSaved_ = false;
};